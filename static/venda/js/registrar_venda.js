
document.addEventListener("DOMContentLoaded", function () {
    const dadosGerais = JSON.parse(document.getElementById('dados-gerais').textContent)[0]; // EXISTENTE
    const dadosClientes = JSON.parse(document.getElementById('dados-clientes').textContent); // ADICIONADO
    const dadosItens = JSON.parse(document.getElementById('dados-itens').textContent); // ADICIONADO

    // Atualizar cabeçalho
    const header = document.querySelector("header p");
    header.textContent = `ID da Venda: ${dadosGerais.id_venda} - Data: ${dadosGerais.data} - Operador: ${dadosGerais.operador}`;

    // Preencher select de clientes
    document.querySelectorAll('select[name="id_cliente"]').forEach(select => { // ADICIONADO
        dadosClientes.forEach(cliente => {
            const option = document.createElement('option');
            option.value = cliente.id;
            option.textContent = `${cliente.id}`;
            select.appendChild(option);
        });
        select.addEventListener("change", function () {
            const selected = dadosClientes.find(c => c.id === this.value);
            const nomeInput = this.closest(".cliente-group").querySelector('input[name="nome_cliente"]');
            if (selected) nomeInput.value = selected.nome;
            else nomeInput.value = "";
        });
    });

    // Preencher selects de código manual
    const codigoSelects = document.querySelectorAll('select[name="codigo[]"]'); // ADICIONADO
    codigoSelects.forEach(select => {
        dadosItens.forEach(item => {
            const option = document.createElement('option');
            option.value = item.codigo;
            option.textContent = `${item.codigo}`;
            select.appendChild(option);
        });
    });

    // Preencher selects de código manual
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



function alternarModo(modo) {
    const formManual = document.getElementById("form-manual");
    const formLeitor = document.getElementById("form-leitor");

    if (modo === "manual") {
        formManual.style.display = "block";
        formLeitor.style.display = "none";
    } else {
        formManual.style.display = "none";
        formLeitor.style.display = "block";
        setTimeout(() => document.getElementById("entrada-leitor").focus(), 100);
    }
}





function adicionarItemManual() {
    const dadosItens = JSON.parse(document.getElementById('dados-itens').textContent); // ADICIONADO
    const container = document.getElementById('itens-manual');
    const novaLinha = document.createElement('div');
    novaLinha.className = 'item-row';
    novaLinha.innerHTML = `
        <div>
            <select name="codigo[]" class="codigo-select" placeholder="Código do item" oninput="atualizarDescricaoValor(this)" style="width: 200px;">
                <option></option>
            </select>
        </div>
        <div>
            <select name="descricao[]" class="descricao-select" placeholder="Descrição do item" oninput="atualizarCodigoValor(this)" style="width: 500px;">
                <option></option>
            </select>
        </div>
            <div><input type="text" name="valor[]" placeholder="Valor (R$)" readonly style="width: 75px"></div>
            <div><input type="number" name="quantidade[]" placeholder="Qtd" min="1" value="1" style="width: 35px"></div>
        </div>
    `;
    container.appendChild(novaLinha);

    // Popular select de código da nova linha
    const selectCodigo = novaLinha.querySelector('select[name="codigo[]"]'); // ADICIONADO
    dadosItens.forEach(item => {
        const option = document.createElement('option');
        option.value = item.codigo;
        option.textContent = `${item.codigo}`;
        selectCodigo.appendChild(option);
    });

    // Popular select de descrição da nova linha
    const selectDescricao = novaLinha.querySelector('select[name="descricao[]"]'); // ADICIONADO
    dadosItens.forEach(item => {
        const option = document.createElement('option');
        option.value = item.descricao;
        option.textContent = `${item.descricao}`;
        selectDescricao.appendChild(option);
    });
    calcularValorTotal();
}







function adicionarItemLeitor(codigo = "") {
    const container = document.getElementById('itens-leitor');
    const novaLinha = document.createElement('div');
    novaLinha.className = 'item-row';
    novaLinha.innerHTML = `
        <div><input type="text" name="codigo[]" placeholder="Código do item" value="${codigo}" readonly style="width: 175px"></div>
        <div><input type="text" name="descricao[]" placeholder="Descrição" readonly style="width: 500px"></div>
        <div><input type="text" name="valor[]" placeholder="Valor (R$)" readonly style="width: 75px"></div>
        <div><input type="number" name="quantidade[]" placeholder="Qtd" min="1" value="1" style="width: 35px"></div>
    `;
    container.appendChild(novaLinha);

    const novaDescricao = novaLinha.querySelector('input[name="descricao[]"]');
    const novoValor = novaLinha.querySelector('input[name="valor[]"]');
    novaDescricao.value = "ITEM CÓDIGO: "+ codigo;
    novoValor.value = "R$ " + 3.00;
    calcularValorTotal();
}





function verificarEnterLeitor(e) {
    if (e.key === 'Enter') {
        e.preventDefault();
        const codigoLido = e.target.value.trim();
        if (!codigoLido) return;

        const camposCodigo = Array.from(document.querySelectorAll('#itens-leitor input[name="codigo[]"]'));

        for (let i = 0; i < camposCodigo.length; i++) {
            if (camposCodigo[i].value.trim() === codigoLido) {
                const linha = camposCodigo[i].closest('.item-row');
                const inputQtd = linha.querySelector('input[name="quantidade[]"]');
                inputQtd.value = parseInt(inputQtd.value || "1") + 1;
                e.target.value = "";
                calcularValorTotal();
                return;
            }
        }

        adicionarItemLeitor(codigoLido);
        e.target.value = "";
    }
}


function atualizarCodigoValor(selectDescricao) {
    const dadosItens = JSON.parse(document.getElementById('dados-itens').textContent);
    const descricao = selectDescricao.value.trim();
    const itemRow = selectDescricao.closest('.item-row');
    const codigoSelect = itemRow.querySelector('select[name="codigo[]"]');
    const valorInput = itemRow.querySelector('input[name="valor[]"]');

    if (descricao) {
        const item = dadosItens.find(i => i.descricao === descricao);
        if (item) {
            codigoSelect.value = item.codigo;
            valorInput.value = `R$ ${parseFloat(item.valor).toFixed(2)}`;
        } else {
            codigoSelect.value = "";
            valorInput.value = "R$ 0.00";
        }
    } else {
        codigoSelect.value = "";
        valorInput.value = "";
    }
    calcularValorTotal();
}



function atualizarDescricaoValor(selectCodigo) {
    const dadosItens = JSON.parse(document.getElementById('dados-itens').textContent);
    const codigo = selectCodigo.value.trim();
    const itemRow = selectCodigo.closest('.item-row');
    const descricaoSelect = itemRow.querySelector('select[name="descricao[]"]');
    const valorInput = itemRow.querySelector('input[name="valor[]"]');

    if (codigo) {
        const item = dadosItens.find(i => i.codigo === codigo);
        if (item) {
            descricaoSelect.value = item.descricao;
            valorInput.value = `R$ ${parseFloat(item.valor).toFixed(2)}`;
        } else {
            descricaoSelect.value = "";
            valorInput.value = "R$ 0.00";
        }
    } else {
        descricaoSelect.value = "";
        valorInput.value = "";
    }
    calcularValorTotal();
}

function calcularValorTotal() {
    const formularioVisivel = document.querySelector('form:not([style*="display: none"])');
    const itemRows = formularioVisivel.querySelectorAll('.item-row');

    let total = 0;
    itemRows.forEach(row => {
        const valorInput = row.querySelector('input[name="valor[]"]');
        const quantidadeInput = row.querySelector('input[name="quantidade[]"]');

        const valor = parseFloat((valorInput.value || "0").replace(/[^\d,.-]/g, '').replace(',', '.')) || 0;
        const quantidade = parseInt(quantidadeInput.value) || 0;

        total += valor * quantidade;
    });

    const descontoInput = formularioVisivel.querySelector('input[name="desconto"]');
    const desconto = parseFloat((descontoInput?.value || "0").replace(',', '.')) || 0;

    const totalComDesconto = Math.max(total - desconto, 0);

    const valorTotalElement = formularioVisivel.querySelector('h2[name="valor_total"]');
    if (valorTotalElement)
        valorTotalElement.textContent = `R$ ${totalComDesconto.toFixed(2).replace('.', ',')}`;
}


document.addEventListener('input', function (event) { 
    const isValor = event.target.name === 'valor[]'; 
    const isQuantidade = event.target.name === 'quantidade[]'; 
    const isDesconto = event.target.name === 'desconto'; 
    if (isValor || isQuantidade || isDesconto) { 
        calcularValorTotal(); 
    } 
});