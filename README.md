# 🛠️ Canivete Suiço para Windows

O **Canivete Suiço para Windows** é uma ferramenta desktop profissional desenvolvida em Python para administradores de sistemas e suporte técnico de TI. Ele centraliza as tarefas mais comuns de troubleshooting em uma interface intuitiva e performática.


## 🚀 Funcionalidades Principais

*   **🔌 Redes**: Diagnósticos rápidos (Ping, Tracert, NSLookup) e manutenção (Flush DNS).
*   **👥 Usuários**: Gerenciamento de acessos e listagem de privilégios via `WhoAmI`.
*   **📂 Pastas**: Cálculo de tamanho de diretórios e limpeza rápida de arquivos temporários.
*   **🖥️ Sistema**: Monitoramento em tempo real de CPU, RAM e todos os Discos Locais.
*   **📝 Inventário**: Extração de Serial Number (Service Tag), Modelo da BIOS e Fabricante via PowerShell.

## 🛠️ Tecnologias Utilizadas

*   **Python 3.14+**
*   **CustomTkinter**: Interface moderna e responsiva.
*   **Psutil**: Monitoramento de hardware e recursos.
*   **Subprocess/PowerShell**: Execução de diagnósticos nativos do Windows.
*   **PyInstaller**: Compilação para executável de arquivo único (`.exe`).

## 📦 Como Gerar o Executável

Caso deseje compilar o projeto manualmente, utilize o comando:

```bash
python -m PyInstaller --noconsole --onefile --clean --name "CaniveteSuico" main.py
```

O executável será gerado na pasta `dist/`.

## 🛡️ Requisitos

*   **Windows 10 ou 11**.
*   Para algumas funções (como SFC/DISM ou Limpeza de System Temp), é necessário executar como **Administrador**.

---
*Desenvolvido para facilitar a vida do administrador de redes moderno.*
