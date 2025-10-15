# Microserviço: Farmácia & Prescrição

## Visão Geral do Projeto

Este repositório contém o desenvolvimento do microserviço de **Farmácia & Prescrição**, componente do sistema de gestão hospitalar proposto para a disciplina de **Arquitetura de Sistemas**.

O objetivo deste serviço é gerenciar de forma autônoma e resiliente todo o ciclo de vida de medicamentos dentro do hospital, desde o seu cadastro no catálogo até a sua dispensação para o paciente, garantindo a integridade e a segurança dos dados clínicos.

## Responsabilidades do Serviço

O serviço foi projetado para cobrir quatro áreas de responsabilidade principais:

<details>
<summary><strong>1. Gerenciamento do Catálogo de Fármacos</strong></summary>

* Manter um repositório centralizado e atualizado de todos os medicamentos disponíveis.
* Prover operações de CRUD (Create, Read, Update, Delete) para os fármacos.
* Implementar um mecanismo de busca de alta performance, com funcionalidades de autocompletar e busca por princípio ativo, utilizando o **Elasticsearch**.

</details>

<details>
<summary><strong>2. Gestão de Prescrições Eletrônicas</strong></summary>

* Permitir que profissionais de saúde autorizados criem prescrições eletrônicas para pacientes.
* Armazenar de forma segura e estruturada os dados da prescrição, incluindo paciente, médico, medicamento, posologia e duração do tratamento.
* Garantir a integridade referencial e a consistência das prescrições no banco de dados transacional.

</details>

<details>
<summary><strong>3. Controle de Dispensação de Medicamentos</strong></summary>

* Registrar a entrega (dispensação) de um medicamento associado a uma prescrição válida.
* Manter o status da prescrição atualizado (ex: "Pendente", "Dispensada", "Cancelada").
* Gerar um histórico de dispensações para fins de auditoria e faturamento.

</details>

<details>
<summary><strong>4. Validação de Regras Clínicas e Interações</strong></summary>

* Implementar lógicas de negócio para auxiliar na segurança do paciente.
* Validar prescrições contra possíveis interações medicamentosas conhecidas.
* Integrar-se (via eventos ou API) com o serviço de **Pacientes & Prontuário** para verificar alergias antes de validar uma nova prescrição.

</details>


___________________________________________________

## Arquitetura e Stack de Tecnologias

A arquitetura deste microserviço segue os princípios de *Domain-Driven Design (DDD)* e *Event-Driven Architecture (EDA)*.



### Endpoints da API

O serviço expõe os seguintes recursos através de sua API:

  * `/medications`: Interação com o catálogo de fármacos.
  * `/prescriptions`: Criação e consulta de prescrições médicas.
  * `/dispensations`: Registro da dispensação de medicamentos.

### Eventos

Para comunicação assíncrona e desacoplada com outros microserviços, este serviço publica os seguintes eventos:

  * `MedicationPrescribed`: Emitido quando uma nova prescrição é criada com sucesso.
  * `MedicationDispensed`: Emitido quando um medicamento é entregue ao paciente.

___________________________________________________

## Membros do Grupo

  * Matheus Veríssimo
  * Gabriel Martins
  * Rafael Angelim
  * Rafael Sampaio
