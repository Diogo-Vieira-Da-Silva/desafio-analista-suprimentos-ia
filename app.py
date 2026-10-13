import os
import pandas as pd
import streamlit as st

EXCEL_FILE = "base_cadastro_e_requisies_1.xlsx"


def carregar_dados():
  if not os.path.exists(EXCEL_FILE):
    st.error(f"Arquivo {EXCEL_FILE} não encontrado na pasta!")
    return None, None, None

  xls = pd.ExcelFile(EXCEL_FILE)
  df_itens = pd.read_excel(xls, "BASE_CADASTRO_ITENS")
  df_rcs = pd.read_excel(xls, "BASE_RCs")

  if "EXCECOES_RCs" in xls.sheet_names:
    df_excecoes = pd.read_excel(xls, "EXCECOES_RCs")
  else:
    df_excecoes = pd.DataFrame(columns=["RC", "Grupo Comprador Exceção"])

  return df_itens, df_rcs, df_excecoes


def salvar_dados(df_itens, df_rcs, df_excecoes):
  with pd.ExcelWriter(EXCEL_FILE, engine="openpyxl") as writer:
    df_itens.to_excel(writer, sheet_name="BASE_CADASTRO_ITENS", index=False)
    df_rcs.to_excel(writer, sheet_name="BASE_RCs", index=False)
    df_excecoes.to_excel(writer, sheet_name="EXCECOES_RCs", index=False)


st.set_page_config(
    page_title="Gestão de Suprimentos - IA", layout="centered"
)

st.title("📦 Aplicação de Suprimentos - Redirecionamento e Cadastro")
st.write(
    "Ferramenta para gestão de Grupo Comprador em RCs e Cadastro de Itens."
)

df_itens, df_rcs, df_excecoes = carregar_dados()

if df_itens is not None:
  st.sidebar.header("Navegação")
  opcao = st.sidebar.selectbox(
      "Escolha a Operação",
      ["Redirecionamento de RC (Exceção)", "Correção de Cadastro de Item"],
  )

  st.divider()

  # ----------------------------------------------------
  # OPERAÇÃO 1: Redirecionamento de RC por Exceção
  # ----------------------------------------------------
  if opcao == "Redirecionamento de RC (Exceção)":
    st.subheader("🔄 Redirecionamento de RC por Exceção")
    st.write(
        "Informe uma ou mais RCs (separadas por vírgula ou espaço) e o novo"
        " Grupo Comprador."
    )

    rcs_input = st.text_input(
        "Número(s) da(s) RC(s) (ex: 10057937, 10054159):"
    )
    novo_grupo_rc = st.text_input("Novo Grupo Comprador:")

    if st.button("Executar Redirecionamento"):
      if not rcs_input.strip() or not novo_grupo_rc.strip():
        st.error(
            "Erro: Informe os números das RCs e o novo Grupo Comprador."
        )
      else:
        try:
          novo_grupo_int = int(novo_grupo_rc)
        except ValueError:
          st.error("Erro: O Grupo Comprador deve ser um número inteiro.")
          st.stop()

        # Tratar lista de RCs informadas
        rcs_lista = []
        for r in rcs_input.replace(",", " ").split():
          try:
            rcs_lista.append(int(r.strip()))
          except ValueError:
            pass

        rcs_encontradas = 0
        mensagens_erro = []

        for rc_alvo in rcs_lista:
          # Verificar se a RC existe na base
          if rc_alvo not in df_rcs["RC"].values:
            mensagens_erro.append(f"RC {rc_alvo} não encontrada.")
            continue

          rcs_encontradas += 1

          # Atualizar BASE_RCs para essa RC
          df_rcs.loc[df_rcs["RC"] == rc_alvo, "Grupo Comprador"] = (
              novo_grupo_int
          )

          # Atualizar ou inserir em EXCECOES_RCs
          if rc_alvo in df_excecoes["RC"].values:
            df_excecoes.loc[
                df_excecoes["RC"] == rc_alvo, "Grupo Comprador Exceção"
            ] = novo_grupo_int
          else:
            nova_linha = pd.DataFrame(
                [{"RC": rc_alvo, "Grupo Comprador Exceção": novo_grupo_int}]
            )
            df_excecoes = pd.concat(
                [df_excecoes, nova_linha], ignore_index=True
            )

        if rcs_encontradas > 0:
          salvar_dados(df_itens, df_rcs, df_excecoes)
          st.success(
              f"Sucesso! {rcs_encontradas} RC(s) redirecionada(s) para o grupo"
              f" {novo_grupo_int}."
          )

        if mensagens_erro:
          for err in mensagens_erro:
            st.warning(err)

  # ----------------------------------------------------
  # OPERAÇÃO 2: Correção do Cadastro de um Item
  # ----------------------------------------------------
  elif opcao == "Correção de Cadastro de Item":
    st.subheader("🛠️ Correção do Cadastro de um Item")
    st.write(
        "Altera o grupo comprador do item e atualiza as RCs associadas (exceto"
        " aquelas com exceção ativa)."
    )

    codigo_item_input = st.text_input("Código do Item:")
    novo_grupo_item = st.text_input("Novo Grupo Comprador do Item:")

    if st.button("Executar Correção de Cadastro"):
      if not codigo_item_input.strip() or not novo_grupo_item.strip():
        st.error("Erro: Informe o código do item e o novo Grupo Comprador.")
      else:
        try:
          cod_item_int = int(codigo_item_input.strip())
          novo_grupo_int = int(novo_grupo_item.strip())
        except ValueError:
          st.error(
              "Erro: O Código do Item e o Grupo Comprador devem ser números"
              " inteiros."
          )
          st.stop()

        # Verificar se o item existe no cadastro
        if cod_item_int not in df_itens["Código item"].values:
          st.error(f"Erro: Item {cod_item_int} não encontrado no cadastro.")
        else:
          # 1. Alterar o Grupo Comprador na aba BASE_CADASTRO_ITENS
          df_itens.loc[
              df_itens["Código item"] == cod_item_int, "Grupo Comprador"
          ] = novo_grupo_int

          # 2. Identificar RCs que possuem exceção cadastrada
          rcs_com_excecao = (
              df_excecoes["RC"].values if not df_excecoes.empty else []
          )

          # 3. Atualizar as linhas da aba BASE_RCs que utilizam esse item, EXCETO se a RC tiver exceção
          # Vamos iterar ou aplicar máscara condicional
          mask_item = df_rcs["Código item"] == cod_item_int
          rcs_afetadas = df_rcs[mask_item]

          atualizadas_count = 0
          ignoradas_excecao = 0

          for idx, row in rcs_afetadas.iterrows():
            rc_num = row["RC"]
            if rc_num in rcs_com_excecao:
              ignoradas_excecao += 1
            else:
              df_rcs.at[idx, "Grupo Comprador"] = novo_grupo_int
              atualizadas_count += 1

          salvar_dados(df_itens, df_rcs, df_excecoes)

          st.success(
              f"Cadastro do item {cod_item_int} atualizado para o grupo"
              f" {novo_grupo_int} com sucesso!"
          )
          st.info(
              f"• RCs atualizadas nas linhas correspondentes:"
              f" {atualizadas_count}\n• RCs ignoradas por possuírem exceção:"
              f" {ignoradas_excecao}"
          )

  st.divider()
  with st.expander("Visualizar Dados Atuais"):
    st.markdown("### Base Cadastro Itens")
    st.dataframe(df_itens)
    st.markdown("### Base RCs")
    st.dataframe(df_rcs)
    if not df_excecoes.empty:
      st.markdown("### Exceções de RCs")
      st.dataframe(df_excecoes)