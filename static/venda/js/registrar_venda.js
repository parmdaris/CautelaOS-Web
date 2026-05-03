const dadosGerais = JSON.parse(document.getElementById('dados-gerais').textContent)[0]; // EXISTENTE
const dadosClientes = JSON.parse(document.getElementById('dados-clientes').textContent); // ADICIONADO
const dadosItens = JSON.parse(document.getElementById('dados-itens').textContent); // ADICIONADO
const listaVendedores = JSON.parse(document.getElementById('lista-vendedores').textContent); // ADICIONADO

function formatarMoeda(v) {
    return "R$ " + parseFloat(v).toFixed(2).replace(".", ",");
}

function limparMoeda(v) {
    return parseFloat(
        v.replace(/[^\d,]/g, "").replace(",", ".")
    ) || 0;
}

function acionarAdicaoManual() { 
    const container = document.getElementById('div-item-manual');
    container.innerHTML = '';
    const linhaManual = document.createElement('div');
    linhaManual.className = 'item-row';
    linhaManual.innerHTML = `
        <div>
            <label>Código</label>
            <select name="codigo[]" id="cod_item" class="codigo-select" placeholder="Código do item" oninput="atualizarDescricaoValor(this)" style="width: 137px;" required>
                <option></option>
            </select>
        </div>

        <div>
        <label>Descrição</label>
            <select name="descricao[]" class="descricao-select" placeholder="Descrição do item" oninput="atualizarCodigoValor(this)" required>
                <option></option>
            </select>
        </div>

        <div>
            <label>Varejo</label>
            <input type="text" name="valor[]" placeholder="Valor (R$)" readonly>
        </div>

        <div>
            <label>Atacado</label>
            <input type="text" name="valor_atacado[]" placeholder="Atacado (R$)" readonly>
        </div>
        
        <div>
            <label>Qtd.</label>
            <input type="number" name="quantidade[]" placeholder="Qtd" min="1" value="1" required>
        </div>
            
            <div>
            
                <button type="button" class="btn-add" onclick="
                    const codigo = this.closest('.item-row')
                    .querySelector('select[name=\\'codigo[]\\']').value;
                    if (!codigo) {
                        alert('Selecione um código primeiro');
                        return;
                    }

                    const quantidade = this.closest('.item-row')
                    .querySelector('input[name=\\'quantidade[]\\']').value;

                    verificarItem(codigo, quantidade);
                    resetAdicaoManual();
                ">+</button>
            </div>

            <div>
            
                <button type="button" class="btnremove" onclick="
                        resetAdicaoManual()
                ">x</button>
            </div>
            
        </div>
    `;
    
    const selectCodigo = linhaManual.querySelector('select[name="codigo[]"]');
    const usados = getCodigosCarrinho();

    dadosItens.forEach(item => {
        const option = document.createElement('option');
        option.value = item.codigo;
        option.textContent = item.codigo;

        if (usados.includes(String(item.codigo))) {
            option.disabled = true;
        }

        selectCodigo.appendChild(option);
    });

    const selectDescricao = linhaManual.querySelector('select[name="descricao[]"]');
    dadosItens.forEach(item => {
        const option = document.createElement('option');
        option.value = item.descricao;
        option.textContent = item.descricao;

        if (usados.includes(String(item.codigo))) {
            option.disabled = true;
        }

        selectDescricao.appendChild(option);
    });

    container.appendChild(linhaManual);

    const qtdManual = linhaManual.querySelector('input[name="quantidade[]"]');
    const codManual = linhaManual.querySelector('select[name="codigo[]"]');

    qtdManual.addEventListener("input", () =>
        atualizarPrecoManual(linhaManual)
    );

    codManual.addEventListener("change", () =>
        atualizarPrecoManual(linhaManual)
    );

    document.getElementById('div-item-manual').style.display = 'inline-block';
    document.getElementById('botao-additem').style.display = 'none';
    document.getElementById('div-leitora').style.display = 'none';
}

function resetAdicaoManual() {
    document.getElementById('div-item-manual').innerHTML = '';
    document.getElementById('div-item-manual').style.display = 'none';
    document.getElementById('botao-additem').style.display = 'inline-block';
    document.getElementById('div-leitora').style.display = '';
    focoLeitor();
}

function addlistaCarrinho(codigo, quantidade) {
    const container = document.getElementById('itens-carrinho');
    const novaLinhaCarrinho = document.createElement('div');
    novaLinhaCarrinho.className = 'item-row';
    novaLinhaCarrinho.innerHTML = `
        <div><input type="text" name="codigo[]" placeholder="Código do item" value="${codigo}" readonly></div>
        <div><input type="text" name="descricao[]" placeholder="Descrição" readonly></div>
        <div><input type="text" name="valor[]" placeholder="Valor (R$)" readonly></div>
        <div><input type="number" name="quantidade[]" placeholder="Qtd" min="1" value="1"></div>
        <div><button type="button" class="btnremove" onclick="removerItemCarrinho(this)">x</button></div>
    `;

    const desc = novaLinhaCarrinho.querySelector('input[name="descricao[]"]');
    const valor = novaLinhaCarrinho.querySelector('input[name="valor[]"]');
    const qtd = novaLinhaCarrinho.querySelector('input[name="quantidade[]"]');

    const item = dadosItens.find(i => String(i.codigo) === String(codigo));
    if (!item) return;

    desc.value = item.descricao;
    valor.value = formatarMoeda(limparMoeda(item.valor));
    qtd.value = quantidade;

    qtd.addEventListener("input", () =>
        atualizarPrecoLinha(novaLinhaCarrinho)
    );

    atualizarPrecoLinha(novaLinhaCarrinho);

    container.appendChild(novaLinhaCarrinho);
    calcularValorTotal();
}

function removerItemCarrinho(botao) {
    const linha = botao.closest('.item-row');
    if (linha) {
        linha.remove();
        calcularValorTotal();
    }
}

function adicionarLeitura(e) {
    if (e.key === 'Enter') {
        e.preventDefault();
        const codigoLido = e.target.value.trim();
        e.target.value = "";
        if (!codigoLido) return;
        verificarItem(codigoLido, 1);
    }
}

function verificarItem(cod_lido, quantidade) {
    const codigosExistentes = Array.from(
        document.querySelectorAll('#itens-carrinho input[name="codigo[]"]')
    );

    for (let cod_existente of codigosExistentes) {
        if (String(cod_existente.value) === String(cod_lido)) {
            const linha = cod_existente.closest('.item-row');
            const qtdExistente = linha.querySelector('input[name="quantidade[]"]');
            qtdExistente.value = (Number(qtdExistente.value) || 0) + (Number(quantidade) || 0);
            atualizarPrecoLinha(linha);
            return true;
        }
    }

    addlistaCarrinho(cod_lido, quantidade);
    return false;
}

function atualizarCodigoValor(selectDescricao) {
    const descricao = selectDescricao.value.trim();
    const row = selectDescricao.closest('.item-row');
    const codigoSelect = row.querySelector('select[name="codigo[]"]');
    const valor = row.querySelector('input[name="valor[]"]');
    const atac = row.querySelector('input[name="valor_atacado[]"]');

    const item = dadosItens.find(i => i.descricao === descricao);

    if (item) {
        codigoSelect.value = item.codigo;
        valor.value = formatarMoeda(limparMoeda(item.valor));
        atac.value = formatarMoeda(limparMoeda(item.valor_atacado));
    } else {
        codigoSelect.value = "";
        valor.value = "";
        atac.value = "";
    }

    calcularValorTotal();
    atualizarPrecoManual(row);
}

function atualizarDescricaoValor(selectCodigo) {
    const codigo = selectCodigo.value.trim();
    const row = selectCodigo.closest('.item-row');
    const descricao = row.querySelector('select[name="descricao[]"]');
    const valor = row.querySelector('input[name="valor[]"]');
    const atac = row.querySelector('input[name="valor_atacado[]"]');

    const item = dadosItens.find(i => String(i.codigo) === String(codigo));

    if (item) {
        descricao.value = item.descricao;
        valor.value = formatarMoeda(limparMoeda(item.valor));
        atac.value = formatarMoeda(limparMoeda(item.valor_atacado));
    } else {
        descricao.value = "";
        valor.value = "";
        atac.value = "";
    }

    calcularValorTotal();
    atualizarPrecoManual(row);
}



function getCodigosCarrinho() {
    return Array.from(
        document.querySelectorAll('#itens-carrinho input[name="codigo[]"]')
    ).map(el => String(el.value));
}



function atualizarPrecoLinha(row) {
    const codigo = row.querySelector('input[name="codigo[]"]').value;
    const qtdInput = row.querySelector('input[name="quantidade[]"]');
    const valorInput = row.querySelector('input[name="valor[]"]');

    const item = dadosItens.find(i => String(i.codigo) === String(codigo));
    if (!item) return;

    const qtd = parseInt(qtdInput.value) || 0;

    qtdInput.max = item.qtd;/*Limita a quantidade selecionável a quantidade em estoque*/

    if (qtd > item.qtd) {
        qtdInput.value = item.qtd;
    }

    let preco;

    if (qtd >= item.qtd_atacado) {
        preco = limparMoeda(item.valor_atacado);
        valorInput.style.background = "#d4ffd4";
    } else {
        preco = limparMoeda(item.valor);
        valorInput.style.background = "#fff";
    }

    valorInput.value = formatarMoeda(preco);
}

function atualizarPrecoManual(row) {
    const codigo = row.querySelector('select[name="codigo[]"]').value;
    const qtdInput = row.querySelector('input[name="quantidade[]"]');
    const valor = row.querySelector('input[name="valor[]"]');
    const atac = row.querySelector('input[name="valor_atacado[]"]');

    const item = dadosItens.find(i => String(i.codigo) === String(codigo));
    if (!item) return;

    const qtd = parseInt(qtdInput.value) || 0;

    qtdInput.max = item.qtd; /*Limita a quantidade selecionável a quantidade em estoque*/

    if (qtd > item.qtd) {
        qtdInput.value = item.qtd;
    }

    valor.value = formatarMoeda(limparMoeda(item.valor));
    atac.value = formatarMoeda(limparMoeda(item.valor_atacado));

    valor.style.background = "#fff";
    atac.style.background = "#fff";

    if (qtd >= item.qtd_atacado) atac.style.background = "#d4ffd4";
    else valor.style.background = "#d4ffd4";
}

function calcularValorTotal() {
    const form = document.querySelector('form[id="formulario"]');
    if (!form) return;

    const rows = form.querySelectorAll('#itens-carrinho .item-row');

    let total = 0;

    rows.forEach(row => {
        const valor = limparMoeda(row.querySelector('input[name="valor[]"]').value || "0");
        const qtd = parseInt(row.querySelector('input[name="quantidade[]"]').value) || 0;
        total += valor * qtd;
    });

    const desconto = limparMoeda(form.querySelector('input[name="desconto"]')?.value || "0");

    const totalFinal = Math.max(total - desconto, 0);

    const el = form.querySelector('h2[name="valor_total"]');
    if (el) el.textContent = formatarMoeda(totalFinal);
}

document.addEventListener('input', function (event) {

    if (event.target.name === 'quantidade[]') {

        const row = event.target.closest('.item-row');

        if (row.querySelector('input[name="codigo[]"]')) atualizarPrecoLinha(row);
        if (row.querySelector('select[name="codigo[]"]')) atualizarPrecoManual(row);
        calcularValorTotal()
    }

    if (event.target.name === 'desconto') calcularValorTotal();
});

function atualizarIdCliente(selectNomeCliente) {
    const nome = selectNomeCliente.value.trim();
    const row = selectNomeCliente.closest('.cliente-group');
    const idSelect = row.querySelector('select[name="id_cliente[]"]');

    const cliente = dadosClientes.find(c => c.nome === nome);
    idSelect.value = cliente ? cliente.id : "";
}

function atualizarNomeCliente(selectIdCliente) {
    const id = selectIdCliente.value.trim();
    const row = selectIdCliente.closest('.cliente-group');
    const nomeSelect = row.querySelector('select[name="nome_cliente[]"]');

    const cliente = dadosClientes.find(c => String(c.id) === String(id));
    nomeSelect.value = cliente ? cliente.nome : "";
}

function focoLeitor(){
    const leitor = document.getElementById("entrada-leitor");
    if (leitor) leitor.focus();
}

document.addEventListener("DOMContentLoaded", function () {

    focoLeitor();
    
    const header = document.querySelector("header p");
    header.textContent = `ID da Venda: ${dadosGerais.id_venda} - Data: ${dadosGerais.data} - Operador: ${dadosGerais.operador}`;

    document.querySelectorAll('select[name="id_cliente[]"]').forEach(select => {
        dadosClientes.forEach(cliente => {
            const option = document.createElement('option');
            option.value = cliente.id;
            option.textContent = cliente.id;
            select.appendChild(option);
        });
    });

    document.querySelectorAll('select[name="nome_cliente[]"]').forEach(select => {
        dadosClientes.forEach(cliente => {
            const option = document.createElement('option');
            option.value = cliente.nome;
            option.textContent = cliente.nome;
            select.appendChild(option);
        });
    });


    document.querySelectorAll('select[name="vendedor"]').forEach(select => {
        listaVendedores.forEach(vendedor => {
            const option = document.createElement('option');
            option.value = vendedor.id;
            option.textContent = vendedor.apelido;
            select.appendChild(option);
        });
    });

    
    document.querySelectorAll('select[name="codigo[]"]').forEach(select => {
        dadosItens.forEach(item => {
            const option = document.createElement('option');
            option.value = item.codigo;
            option.textContent = item.codigo;
            select.appendChild(option);
        });
    });

    document.querySelectorAll('select[name="descricao[]"]').forEach(select => {
        dadosItens.forEach(item => {
            const option = document.createElement('option');
            option.value = item.descricao;
            option.textContent = item.descricao;
            select.appendChild(option);
        });
    });
});
