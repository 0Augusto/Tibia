# Calculadora de Dano - Tibia

![Tibia](https://img.shields.io/badge/Tibia-Hunt%20Calculator-green)
![License](https://img.shields.io/badge/License-Apache%202.0-blue)

**Criado por Cedine Rush**

Aplicação desktop para cálculo de dano por hora em caçadas (hunts) no jogo Tibia. O programa permite configurar os atributos do personagem, gerenciar múltiplas hunts e seus respectivos monstros, e calcular o dano físico, dano de runas e totais por hora, considerando leech e dano crítico.

Os dados são armazenados em um banco de dados SQLite local, garantindo persistência entre sessões.

---

## Funcionalidades

- **Configuração do Personagem**
  - Ataque base (Attack Value + Auto-Attack Extra Damage)
  - Chance e dano extra de crítico
  - Life Leech e Mana Leech (percentuais)
  - Taxa de ataques por minuto

- **Gerenciamento de Hunts**
  - Criação, edição e exclusão de diferentes localidades de caça
  - Seleção da hunt atual via combobox
  - Persistência em banco de dados SQLite

- **Gerenciamento de Monstros**
  - Adicionar, editar e remover monstros da hunt atual
  - Para cada monstro: nome, quantidade por hora, vida, fraqueza (multiplicador), tipo de runa
  - Tipos de runa suportados:
    - **Normal**: 5% da vida
    - **Low Blow**: 8% da vida
    - **Savage Blow**: 40% da vida
  - Cálculo automático do dano por runa (aplicando fraqueza)

- **Cálculo de Dano**
  - Dano médio por ataque (considerando crítico)
  - Leech médio por ataque
  - Dano físico por hora (baseado na taxa de ataques)
  - Dano total de runas por hora (somatório para todos os monstros)
  - Dano total combinado por hora

- **Interface Gráfica**
  - Construída com Tkinter
  - Exibição em tabela (Treeview) com dano por mob e total por hunt
  - Botões intuitivos para todas as operações

---

## Como Usar

### Pré-requisitos
- Python 3.6 ou superior instalado
- Tkinter (geralmente incluso na instalação padrão do Python)

### Instalação
1. Clone o repositório ou faça o download dos arquivos.
2. Navegue até a pasta do projeto.
3. Execute o programa:
   ```bash
   python damage_calculator.py
