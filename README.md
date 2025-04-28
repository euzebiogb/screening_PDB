# Script de Triagem Virtual Baseada no Ligante (make_LIGAND_based_screen.sh)

Este script Bash realiza uma triagem virtual baseada nas características do ligante (molécula de consulta). Ele calcula um descritor de forma/volume ("sphere count") para a molécula de consulta, filtra um banco de dados de moléculas com base nesse descritor e, em seguida, realiza uma comparação de forma 3D usando LSalign entre a consulta e as moléculas filtradas.

## Funcionalidades

* Converte a molécula de consulta de vários formatos (SDF, MOL2, PDB, etc.) para SDF, se necessário.
* Calcula um descritor "sphere count" para a molécula de consulta usando um script Python auxiliar.
* Identifica moléculas em um banco de dados SDF principal que possuem um "sphere count" similar (usando scripts Python auxiliares).
* Filtra o banco de dados principal para extrair apenas as moléculas candidatas.
* Converte a molécula de consulta e as moléculas filtradas para o formato MOL2.
* Realiza comparação de forma 3D entre a consulta e cada molécula filtrada usando LSalign.
* Salva os resultados brutos do LSalign em um arquivo de texto.
* Limpa automaticamente os arquivos intermediários gerados.

## Dependências

### Software Externo

* **Bash:** O interpretador de comandos shell.
* **Python 3:** Necessário para executar os scripts auxiliares `.py`.
* **Open Babel:** Necessário para conversões de formato de arquivo molecular (`obabel`). Deve estar no `PATH`.
* **LSalign:** Necessário para a comparação de forma 3D. Deve estar no `PATH`.
* **Utilitários Unix Padrão:** `basename`, `rm`, `cat`, `tail`, `awk`, `command`.

### Scripts Python Auxiliares

Este script principal depende de vários scripts Python auxiliares que devem estar no mesmo diretório ou em um local acessível pelo `PATH`:

* `sphere_count.py`: Calcula o descritor "sphere count" para uma molécula em formato SDF.
* `get_s_count.py`: Gera uma lista de IDs de moléculas com base em um valor de "sphere count".
* `filter_sdf.py`: Filtra um arquivo SDF principal com base em uma lista de IDs fornecida.

### Arquivos de Dados

* **Banco de Dados SDF Principal:** O script utiliza um caminho **hardcoded** para o banco de dados principal: `./Components-pub_fix.sdf`. Este arquivo **deve** existir neste local relativo ou o caminho no script precisa ser modificado.

## Instalação

1.  **Instale as Dependências de Software:** Instale Python 3, Open Babel e LSalign usando os gerenciadores de pacotes do seu sistema (apt, yum, brew, conda) ou baixando dos sites oficiais. Certifique-se de que os comandos `python3`, `obabel` e `LSalign` estejam acessíveis no `PATH`.
2.  **Obtenha os Scripts Auxiliares:** Certifique-se de que todos os scripts Python listados em [Scripts Auxiliares](#scripts-auxiliares) estejam no mesmo diretório que o script principal (`make_LIGAND_based_screen.sh`) ou em um local incluído no `PATH`.
3.  **Prepare o Banco de Dados:** Coloque o arquivo de banco de dados SDF (`Components-pub_fix.sdf`) no mesmo diretório onde o script será executado, ou ajuste o caminho `./Components-pub_fix.sdf` dentro do script `make_LIGAND_based_screen.sh`.
4.  Download ligands: https://files.wwpdb.org/pub/pdb/data/monomers/components-pub.sdf.gz
5.  **Dê Permissão de Execução:** Torne o script principal executável: `chmod +x make_LIGAND_based_screen.sh`.

## Uso

Execute o script a partir da linha de comando, fornecendo o arquivo da molécula de consulta como único argumento:


  `./make_LIGAND_based_screen.sh <arquivo_de_entrada>`

* Argumento:

<arquivo_de_entrada> (Obrigatório): Caminho para o arquivo contendo a molécula de consulta. Formatos suportados incluem SDF, MOL2, MOL, PDB e outros que o Open Babel consiga ler.

* Exemplo:

  `./make_LIGAND_based_screen.sh minha_molecula_query.mol2`

Formato dos Arquivos
Arquivo de Entrada: Qualquer formato molecular que o Open Babel suporte (SDF, MOL2, PDB, SMILES, etc.).

Banco de Dados SDF Principal (./Components-pub_fix.sdf): Um arquivo multi-molécula em formato SDF padrão.

Arquivo de Saída (result_<basename>.txt): Um arquivo de texto contendo a saída bruta do comando LSalign. O formato exato dependerá da versão e das opções padrão do LSalign, mas geralmente inclui scores de alinhamento (como PC-score, RMSD, etc.) para cada comparação entre a consulta e as moléculas filtradas. <basename> é o nome do arquivo de entrada sem a extensão.

Arquivos Intermediários: O script cria vários arquivos temporários (spheres_input.csv, id.csv, filtered_compounds.sdf, <basename>.sdf, <basename>.mol2, filtered.mol2) que são automaticamente removidos no final da execução ou em caso de erro (via trap).

Descrição do Fluxo de Trabalho
Validação Inicial: Verifica se um arquivo de entrada foi fornecido e se ele existe. Verifica se os programas necessários (python3, obabel, LSalign) estão disponíveis.

* Configuração de Limpeza: Define um trap para garantir que os arquivos intermediários sejam removidos quando o script terminar ou for interrompido.

Conversão para SDF (se necessário): Se o arquivo de entrada não for SDF, usa obabel para convertê-lo para <basename>.sdf.

* Cálculo do Descritor: Executa sphere_count.py no arquivo SDF da consulta para gerar spheres_input.csv.

* Extração do Descritor: Lê o valor do "sphere count" do arquivo spheres_input.csv.

* Geração de IDs: Executa get_s_count.py com o valor do "sphere count" para gerar uma lista de IDs de moléculas candidatas em id.csv.

* Filtragem do Banco de Dados: Executa filter_sdf.py para extrair as moléculas correspondentes aos IDs em id.csv do banco de dados principal (./Components-pub_fix.sdf), salvando-as em filtered_compounds.sdf.

* Conversão para MOL2: Usa obabel para converter filtered_compounds.sdf em filtered.mol2 e o SDF da consulta em <basename>.mol2.

* Comparação 3D: Executa LSalign para comparar a consulta (<basename>.mol2) com o conjunto filtrado (filtered.mol2).

* Salvar Resultados: Redireciona a saída padrão completa do LSalign para o arquivo result_<basename>.txt.

* Limpeza: A função definida pelo trap remove os arquivos intermediários.
