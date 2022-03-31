<h1 style="text-align:center">Book de Turno do Laboratório de Químicos</h1>
<p style="text-align:center">Projeto simples de Otimização de troca de turno no laboratório de Químicos</p>

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) 	![Firebase](https://img.shields.io/badge/firebase-%23039BE5.svg?style=for-the-badge&logo=firebase) ![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)

A aplicação está hospedada na plataforma do Streamlit tendo em vista sua simplicidade.
Ela se divide em - por enquanto - três seções no menu: Home, Inserir e Busca. Pretende-se, ainda, adicionar mais uma seção de análises e outra de ações.

## _Roadmap_

- [x] Múltiplas inserções por turno;
- [ ] Inserir autenticação por ID;
- [ ] Criar seção de Análises;
- [ ] Criar seção de Ações;
- [ ] Analisar viabilidade de migrar a hospedagem para servidor local e MySQL.

## Home

![Home](https://github.com/thinklm/lab-shift-change/blob/main/img/home_screenshot.png)

Nessa tela principal, deverá aparecer o que foi preenchido no _book_ de turno do período anterior, juntando todas as atualizações feitas no mesmo _layout_ que os dados são inseridos.
A partir do momento que algo do turno atual for informado, aparecerá as atualizações desse turno.

## Inserir

![Inserir](https://github.com/thinklm/lab-shift-change/blob/main/img/inserir_screenshot.png)

Nessa tela, um _forms_ permitirá a inserção das informações no banco de dados referente às linhas 571 e 572, estratificado pelos equipamentos Lavadora, SOS e UVBC da produção, junto com campos de texto para observações gerais e pendências **(a modificar)**.

Nessa parte, são criadas chaves para as _tags_ de forma a conseguir identificar

## Buscar

![Buscar](https://github.com/thinklm/lab-shift-change/blob/main/img/buscar_screenshot.png)

Nessa seção, é possível realizar a busca dos dados filtrados por data e turno em seu "formato" final, ou seja, com todas as atualizações realizadas.



