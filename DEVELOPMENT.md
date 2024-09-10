# Desenvolvimento

Este passo-a-passo refere-se às instruções para **desenvolvimento** do pacote. Se você deseja apenas usá-lo, siga para
a seção [Instalação](#instalação).

1. Instale o [Python Anaconda](https://www.anaconda.com/download) na sua máquina
2. Crie o ambiente virtual do anaconda e instale as bibliotecas necessárias com o comando

   ```bash
   conda env create -f environment.yml
   ```

3. Construa o pacote:

   ```bash
   python -m build
   ```

4. Instale-o localmente com 

5. Este repositório já conta com uma GitHub Action para publicar automaticamente no PyPi e TestPyPi. Consulte o arquivo 
   [python-publish.yml](.github/workflows/python-publish.yml) para detalhes da implementação.
  
   Todos os commits serão enviados para o TestPyPi, mas apenas commits com tags serão enviados para o PyPi:

   ```bash
   # alguma modificação no código fonte
   # ...
   git add .
   git commit -m "mensagem do commit"
   git tag -a <tag_name> -m "título da versão"
   git push origin main  # envia o commit para o repositório e o pacote para TestPyPi
   git push origin <tag_name>  # publica a tag e envia o pacote para o PyPi
   ```
   
   Onde <tag_name> é um número no formato, por exemplo, `v1.4.1`.

   Use apenas os comandos `git tag -a <tag_name>` e `git push origin <tag_name>` quando quiser publicar o pacote no 
   canal PyPi! 

   Um tutorial de publicação com GitHub Actions está disponível 
   [neste link](https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/)