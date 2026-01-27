const dadosGerais = JSON.parse(document.getElementById('dados-gerais').textContent)[0]; // EXISTENTE
const dadosClientes = JSON.parse(document.getElementById('dados-clientes').textContent); // ADICIONADO
const dadosItens = JSON.parse(document.getElementById('dados-itens').textContent); // ADICIONADO



function acionarAdicaoManual() { 
    const container = document.getElementById('div-item-manual');
    container.innerHTML = '';
    const linhaManual = document.createElement('div');
    linhaManual.className = 'item-row';
    linhaManual.innerHTML = `
        <div>
            <label>Código</label>
            <select name="codigo[]" id="cod_item" class="codigo-select" placeholder="Código do item" oninput="atualizarDescricaoValor(this)" style="width: 137px;">
                <option></option>
            </select>
        </div>

        <div>
        <label>Descrição</label>
            <select name="descricao[]" class="descricao-select" placeholder="Descrição do item" oninput="atualizarCodigoValor(this)">
                <option></option>
            </select>
        </div>

        <div>
            <label>Varejo</label>
            <input type="text" name="valor[]" placeholder="Valor (R$)" readonly> <!--  style="width: 75px" -->
        </div>

        <div>
            <label>Atacado</label>
            <input type="text" name="valor_atacado[]" placeholder="Atacado (R$)" readonly> <!--  style="width: 75px" -->
        </div>
        
        <div>
            <label>Qtd.</label>
            <input type="number" name="quantidade[]" placeholder="Qtd" min="1" value="1">
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
    

    // Popular select de código da nova linha
    const selectCodigo = linhaManual.querySelector('select[name="codigo[]"]'); // ADICIONADO
    dadosItens.forEach(item => {
        const option = document.createElement('option');
        option.value = item.codigo;
        option.textContent = `${item.codigo}`;
        selectCodigo.appendChild(option);
    });

    // Popular select de descrição da nova linha
    const selectDescricao = linhaManual.querySelector('select[name="descricao[]"]'); // ADICIONADO
    dadosItens.forEach(item => {
        const option = document.createElement('option');
        option.value = item.descricao;
        option.textContent = `${item.descricao}`;
        selectDescricao.appendChild(option);
    });

    container.appendChild(linhaManual);
    document.getElementById('botao-additem').style.display = 'none'; //Esconde o botão de adição manual após o clique
    document.getElementById('div-leitora').style.display = 'none'; //Esconde o campo de leitura via leitor

}


function resetAdicaoManual() {
    document.getElementById('div-item-manual').innerHTML = ''; // remove os campos de adição manual
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
        <div><input type="text" name="valor_atacado[]" placeholder="Atacado (R$)" readonly></div>
        <div><input type="number" name="quantidade[]" placeholder="Qtd" min="1" value="1"></div>
        <div><button type="button" class="btnremove" onclick="removerItemCarrinho(this)">x</button></div>
    `;
    const desc_itemAoCarrinho = novaLinhaCarrinho.querySelector('input[name="descricao[]"]');
    const valor_itemAoCarrinho = novaLinhaCarrinho.querySelector('input[name="valor[]"]');
    const valor_atac_itemAoCarrinho = novaLinhaCarrinho.querySelector('input[name="valor_atacado[]"]');
    const qtd_itemAoCarrinho = novaLinhaCarrinho.querySelector('input[name="quantidade[]"]');

    const item = dadosItens.find(i => String(i.codigo) === String(codigo));
    if (!item) {
        alert(`Item não encontrado: ${codigo}`);
        return;
    }

    desc_itemAoCarrinho.value = item.descricao;
    valor_itemAoCarrinho.value = `R$ ${parseFloat(item.valor).toFixed(2)}`;
    valor_atac_itemAoCarrinho.value = `R$ ${parseFloat(item.valor_atacado).toFixed(2)}`;
    qtd_itemAoCarrinho.value = quantidade;
        
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
        qtd_aoCarrinho = 1;

        verificarItem(codigoLido, qtd_aoCarrinho);
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

            const qtdAtual = Number(qtdExistente.value) || 0;
            const qtdNova = Number(quantidade) || 0;
            qtdExistente.value = qtdAtual + qtdNova;
            calcularValorTotal();
            return true;
        }
    }
    addlistaCarrinho(cod_lido, quantidade);
    return false;
}

function atualizarCodigoValor(selectDescricao) {
    const dadosItens = JSON.parse(document.getElementById('dados-itens').textContent);
    const descricao = selectDescricao.value.trim();
    const itemRow = selectDescricao.closest('.item-row');
    const codigoSelect = itemRow.querySelector('select[name="codigo[]"]');
    const valorInput = itemRow.querySelector('input[name="valor[]"]');
    const valorAtacInput = itemRow.querySelector('input[name="valor_atacado[]"]');


    if (descricao) {
        const item = dadosItens.find(i => i.descricao === descricao);
        if (item) {
            codigoSelect.value = item.codigo;
            valorInput.value = `R$ ${parseFloat(item.valor).toFixed(2)}`;
            valorAtacInput.value = `R$ ${parseFloat(item.valor_atacado).toFixed(2)}`;
        } else {
            codigoSelect.value = "";
            valorInput.value = "R$ 0.00";
            valorAtacInput.value = "R$ 0.00";
        }
    } else {
        codigoSelect.value = "";
        valorInput.value = "";
        valorAtacInput.value = "";
    }
    calcularValorTotal();
}

function atualizarDescricaoValor(selectCodigo) {
    const dadosItens = JSON.parse(document.getElementById('dados-itens').textContent);
    const codigo = selectCodigo.value.trim();
    const itemRow = selectCodigo.closest('.item-row');
    const descricaoSelect = itemRow.querySelector('select[name="descricao[]"]');
    const valorInput = itemRow.querySelector('input[name="valor[]"]');
    const valorAtacInput = itemRow.querySelector('input[name="valor_atacado[]"]');

    if (codigo) {
        const item = dadosItens.find(i => i.codigo === codigo);
        if (item) {
            descricaoSelect.value = item.descricao;
            valorInput.value = `R$ ${parseFloat(item.valor).toFixed(2)}`;
            valorAtacInput.value = `R$ ${parseFloat(item.valor_atacado).toFixed(2)}`;
        } else {
            descricaoSelect.value = "";
            valorInput.value = "R$ 0.00";
            valorAtacInput.value = "R$ 0.00";
        }
    } else {
        descricaoSelect.value = "";
        valorInput.value = "";
        valorAtacInput.value = "";
    }
    calcularValorTotal();
}

function calcularValorTotal() {
    const formularioVisivel = document.querySelector('form[id="formulario"]');
    const itemRows = formularioVisivel.querySelectorAll('#itens-carrinho .item-row');

    let total = 0;

    itemRows.forEach(row => {
        const valorInput = row.querySelector('input[name="valor[]"]');
        const quantidadeInput = row.querySelector('input[name="quantidade[]"]');

        if (!valorInput || !quantidadeInput) return;

        const valor = parseFloat(
            (valorInput.value || "0")
                .replace(/[^\d,.-]/g, '')
                .replace(',', '.')
        ) || 0;

        const quantidade = parseInt(quantidadeInput.value) || 0;
        total += valor * quantidade;
    });

    const descontoInput = formularioVisivel.querySelector('input[name="desconto"]');
    const desconto = parseFloat((descontoInput?.value || "0").replace(',', '.')) || 0;

    const totalComDesconto = Math.max(total - desconto, 0);

    const valorTotalElement = formularioVisivel.querySelector('h2[name="valor_total"]');
    if (valorTotalElement) {
        valorTotalElement.textContent = `R$ ${totalComDesconto.toFixed(2).replace('.', ',')}`;
    }
}

document.addEventListener('input', function (event) {  ////////////////////////////////////////////////////////////////////////////// CONFLITO
    const isValor = event.target.name === 'valor[]'; 
    const isQuantidade = event.target.name === 'quantidade[]'; 
    const isDesconto = event.target.name === 'desconto'; 
    if (isValor || isQuantidade || isDesconto) { 
        calcularValorTotal(); 
    } 
});


const descontoInput = document.querySelector('input[name="desconto"]'); ////////////////////////////////////////////////////////////////////////////// CONFLITO

if (descontoInput) {
    descontoInput.value = "R$ 0,00";

    descontoInput.addEventListener("input", () => {
        let valor = descontoInput.value.replace(/\D/g, "");
        valor = (Number(valor) / 100).toFixed(2).replace(".", ",");
        descontoInput.value = "R$ " + valor;
    });
}



function atualizarIdCliente(selectNomeCliente) {
    const dadosClientes = JSON.parse(
        document.getElementById('dados-clientes').textContent
    );

    const nome = selectNomeCliente.value.trim();

    const clienteRow = selectNomeCliente.closest('.cliente-group');

    const idSelect = clienteRow.querySelector(
        'select[name="id_cliente[]"]'
    );

    if (nome) {
        const cliente = dadosClientes.find(c => c.nome === nome);

        if (cliente) {
            idSelect.value = cliente.id;
        } else {
            idSelect.value = "";
        }
    } else {
        idSelect.value = "";
    }
}


function atualizarNomeCliente(selectIdCliente) {
    const dadosClientes = JSON.parse(
        document.getElementById('dados-clientes').textContent
    );

    const id = selectIdCliente.value.trim();

    const clienteRow = selectIdCliente.closest('.cliente-group');

    const nomeSelect = clienteRow.querySelector(
        'select[name="nome_cliente[]"]'
    );

    if (id) {
        const cliente = dadosClientes.find(
            c => String(c.id) === String(id)
        );

        if (cliente) {
            nomeSelect.value = cliente.nome;
        } else {
            nomeSelect.value = "";
        }
    } else {
        nomeSelect.value = "";
    }
}

function focoLeitor(){
    const leitor = document.getElementById("entrada-leitor"); //Foco no leitor de código ao carregar a página
    if (leitor) {
        leitor.focus();
    }
}

document.addEventListener("DOMContentLoaded", function () {

    focoLeitor();
    
    // Atualizar cabeçalho
    const header = document.querySelector("header p");
    header.textContent = `ID da Venda: ${dadosGerais.id_venda} - Data: ${dadosGerais.data} - Operador: ${dadosGerais.operador}`;

    // Preencher select de ID de clientes -------------------------------------------------------------------------------------------------------------------------------------
    document.querySelectorAll('select[name="id_cliente[]"]').forEach(select => { // ADICIONADO
        dadosClientes.forEach(cliente => {
            const option = document.createElement('option');
            option.value = cliente.id;
            option.textContent = `${cliente.id}`;
            select.appendChild(option);
        });
        select.addEventListener("change", function () {
            const selected = dadosClientes.find(c => c.id === this.value);
            const idSelect = this.closest(".cliente-group").querySelector('select[name="id_cliente"]');
            if (selected) idSelect.value = selected.id;
            else idSelect.value = "";
        });
    });

    // Preencher select de nomes de clientes -------------------------------------------------------------------------------------------------------------------------------------
    document.querySelectorAll('select[name="nome_cliente[]"]').forEach(select => { // ADICIONADO
        dadosClientes.forEach(cliente => {
            const option = document.createElement('option');
            option.value = cliente.nome;
            option.textContent = `${cliente.nome}`;
            select.appendChild(option);
        });
        select.addEventListener("change", function () {
            const selected = dadosClientes.find(c => c.id === this.value);
            const nomeSelect = this.closest(".cliente-group").querySelector('select[name="nome_cliente"]');
            if (selected) nomeSelect.value = selected.nome;
            else nomeInput.value = "";
        });
    });

    // Preencher selects de código manual -------------------------------------------------------------------------------------------------------------------------------------
    const codigoSelects = document.querySelectorAll('select[name="codigo[]"]'); // ADICIONADO
    codigoSelects.forEach(select => {
        dadosItens.forEach(item => {
            const option = document.createElement('option');
            option.value = item.codigo;
            option.textContent = `${item.codigo}`;
            select.appendChild(option);
        });
    });

    // Preencher selects de descrição manual -------------------------------------------------------------------------------------------------------------------------------------
    const descricaoSelects = document.querySelectorAll('select[name="descricao[]"]'); // ADICIONADO
    descricaoSelects.forEach(select => {
        dadosItens.forEach(item => {
            const option = document.createElement('option');
            option.value = item.descricao;
            option.textContent = `${item.descricao}`;
            select.appendChild(option);
        });
    });
});



