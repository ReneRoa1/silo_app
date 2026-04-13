# -*- coding: utf-8 -*-
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from relatorio import gerar_relatorio_pdf
from datetime import datetime
from pathlib import Path
from relatorio import gerar_relatorio_pdf
from calculos import (
    Rebanho,
    Dieta,
    Forragem,
    Operacao,
    calcular_ap_ha,
    calcular_cmi,
    calcular_cmn,
    calcular_comprimento_operacional,
    calcular_cr,
    calcular_ct,
    calcular_cvo,
    calcular_face_minima,
    calcular_ve_t,
    calcular_volume_total_silo,
)
from otimizacao import (
    otimizar_secao_ovalada,
    otimizar_secao_retangular,
    otimizar_secao_trapezoidal,
)
from visualizacao import criar_solido_prismatico, criar_solido_superficie_oval


st.set_page_config(page_title="Dimensionamento de Silo para Silagem", layout="wide")
st.title("Dimensionamento de Silo para Silagem")
st.caption(
    "Interface aprimorada, com termos completos e foco nas informaÃ§Ãµes finais mais Ãºteis para a tomada de decisÃ£o."
)

with st.sidebar:
    st.header("Projeto")
    nome_projeto = st.text_input(
    "Nome da propriedade ou projeto",
    value="Projeto de dimensionamento",
)

    responsavel_tecnico = st.text_input(
    "ResponsÃ¡vel tÃ©cnico",
    value="",
    help="Nome do responsÃ¡vel tÃ©cnico que aparecerÃ¡ no relatÃ³rio em PDF.",
)

    logo_file = st.file_uploader(
    "Logo institucional (opcional)",
    type=["png", "jpg", "jpeg"],
    help="Envie a logo que serÃ¡ exibida no relatÃ³rio em PDF.",
)
    st.header("InformaÃ§Ãµes dos animais")
    numero_animais = st.number_input("Quantidade de animais", min_value=1, value=100, step=1, help="NÃºmero total de animais que irÃ£o consumir a silagem durante o perÃ­odo informado.")
    peso_medio_kg = st.number_input(
    "Peso mÃ©dio (kg)",
    min_value=1.0,
    value=450.0,
    step=10.0,
    help="Peso mÃ©dio dos animais do lote, em quilogramas."
)
    consumo_percent_pv = st.number_input(
        "Consumo de matÃ©ria seca (% do peso vivo)",
        min_value=0.1,
        value=2.5,
        step=0.1,
        help="Consumo diÃ¡rio de matÃ©ria seca expresso como porcentagem do peso vivo."
    )
    volumoso_percent = st.slider("ParticipaÃ§Ã£o do volumoso na dieta (%)", min_value=0, max_value=100, value=60, help="Percentual da matÃ©ria seca da dieta que serÃ¡ fornecido na forma de volumoso.")

    st.header("InformaÃ§Ãµes da forragem e da operaÃ§Ã£o")
    teor_ms_percent = st.number_input(
        "Teor de matÃ©ria seca da forragem (%)",
        min_value=10.0,
        max_value=80.0,
        value=32.0,
        step=0.5,
        help="Percentual de matÃ©ria seca da forragem no momento da ensilagem."
    )
    perdas_percent = st.number_input("Perdas previstas (%)", min_value=0.0, max_value=50.0, value=10.0, step=0.5, help="Percentual estimado de perdas durante armazenamento, manejo e desabastecimento.")
    produtividade_mn_t_ha = st.number_input(
        "Produtividade da forragem (t MN/ha)",
        min_value=1.0,
        value=40.0,
        step=1.0,
        help="Percentual estimado de perdas durante armazenamento, manejo e desabastecimento."
    )
    periodo_dias = st.number_input("PerÃ­odo de fornecimento (dias)", min_value=1, value=180, step=1, help="NÃºmero de dias durante os quais a silagem serÃ¡ fornecida aos animais.")
    desabastecimento_m_dia = st.number_input(
        "Taxa de desabastecimento (m/dia)",
        min_value=0.01,
        value=0.15,
        step=0.01,
        help="AvanÃ§o diÃ¡rio da frente do silo, em metros por dia."
    )
    compactacao_t_m3 = st.number_input(
        "CompactaÃ§Ã£o da silagem (t MN/mÂ³)",
        min_value=0.10,
        value=0.65,
        step=0.01,
        format="%.2f",
        help="Densidade da silagem compactada, em toneladas de matÃ©ria natural por metro cÃºbico."
    )

    st.header("ConfiguraÃ§Ã£o do silo")
    tipo_estrutura = st.selectbox("Tipo estrutural do silo", ["Trincheira", "SuperfÃ­cie"], help="Escolha o tipo estrutural do silo: trincheira ou superfÃ­cie.")
    # lÃ³gica dinÃ¢mica
    if tipo_estrutura == "SuperfÃ­cie":
        opcoes_secao = ["Trapezoidal", "Ovalada"]
    else:
        opcoes_secao = ["Retangular", "Trapezoidal"]
    tipo_secao = st.selectbox("Forma da seÃ§Ã£o transversal", opcoes_secao, help="Define a geometria da seÃ§Ã£o transversal usada no cÃ¡lculo e na visualizaÃ§Ã£o do silo.")
    largura_trator_m = st.number_input("Largura do trator (m)", min_value=0.5, value=2.40, step=0.05, format="%.2f", help="Largura do trator utilizado na compactaÃ§Ã£o, usada como referÃªncia para a largura do silo.")

    with st.expander("OpÃ§Ãµes avanÃ§adas", expanded=False):
        folga_lateral_m = st.number_input(
            "Folga lateral total (m)",
            min_value=0.0,
            value=0.0,
            step=0.1,
            format="%.2f",
            help="Margem adicional aplicada Ã  largura calculada a partir da largura do trator e do nÃºmero de passadas."
        )
        passadas_min = st.number_input(
            "NÃºmero mÃ­nimo de passadas do trator",
            min_value=1,
            value=2,
            step=1,
            help="Menor nÃºmero de passadas do trator considerado na otimizaÃ§Ã£o da largura do silo."
        )
        passadas_max = st.number_input(
            "NÃºmero mÃ¡ximo de passadas do trator",
            min_value=1,
            value=5,
            step=1,
            help="Maior nÃºmero de passadas do trator considerado na otimizaÃ§Ã£o da largura do silo."
        )
        altura_min_m = st.number_input(
            "Altura mÃ­nima do silo (m)",
            min_value=0.5,
            value=2.0,
            step=0.1,
            help="Menor altura do silo que serÃ¡ testada na otimizaÃ§Ã£o."
        )
        altura_max_m = st.number_input(
            "Altura mÃ¡xima do silo (m)",
            min_value=0.5,
            value=4.0,
            step=0.1,
            help="Maior altura do silo que serÃ¡ testada na otimizaÃ§Ã£o."
        )
        passo_altura_m = st.number_input(
            "Intervalo entre alturas testadas na otimizaÃ§Ã£o (m)",
            min_value=0.05,
            value=0.25,
            step=0.05,
            format="%.2f",
            help="Incremento entre as alturas avaliadas durante a otimizaÃ§Ã£o."
        )

        st.markdown("**ParÃ¢metros geomÃ©tricos da seÃ§Ã£o**")

        if tipo_secao == "Trapezoidal":
            talude_h_por_v = st.number_input(
                "RelaÃ§Ã£o do talude horizontal para vertical",
                min_value=0.1,
                value=0.5,
                step=0.1,
                format="%.2f",
                help="RelaÃ§Ã£o usada para definir a abertura lateral do silo trapezoidal. Exemplo: 0,5 significa 0,5 m na horizontal para cada 1 m na vertical."
            )
            largura_topo_min_m = st.number_input(
                "Largura mÃ­nima da base maior ou do topo (m)",
                min_value=0.5,
                value=3.0,
                step=0.1,
                help="Valor mÃ­nimo aceito para a base maior ou topo da seÃ§Ã£o trapezoidal."
            )
        elif tipo_secao == "Ovalada":
            talude_h_por_v = 0.0
            largura_topo_min_m = st.number_input(
                "Largura mÃ­nima da base (m)",
                min_value=0.5,
                value=3.0,
                step=0.1,
                help="Valor mÃ­nimo da base adotado para seÃ§Ãµes ovaladas."
            )
        else:
            talude_h_por_v = 0.0
            largura_topo_min_m = 0.0
            st.caption("A seÃ§Ã£o retangular nÃ£o usa talude nem largura mÃ­nima de topo.")
            

try:
    if passadas_max < passadas_min:
        raise ValueError("O nÃºmero mÃ¡ximo de passadas nÃ£o pode ser menor que o nÃºmero mÃ­nimo.")
    if altura_max_m < altura_min_m:
        raise ValueError("A altura mÃ¡xima nÃ£o pode ser menor que a altura mÃ­nima.")

    rebanho = Rebanho(
        numero_animais=int(numero_animais),
        peso_medio_kg=float(peso_medio_kg),
        consumo_percent_pv=float(consumo_percent_pv),
    )
    dieta = Dieta(volumoso_percent=float(volumoso_percent))
    forragem = Forragem(
        teor_ms_percent=float(teor_ms_percent),
        perdas_percent=float(perdas_percent),
        produtividade_mn_t_ha=float(produtividade_mn_t_ha),
    )
    operacao = Operacao(
        periodo_dias=int(periodo_dias),
        desabastecimento_m_dia=float(desabastecimento_m_dia),
        compactacao_t_m3=float(compactacao_t_m3),
        largura_trator_m=float(largura_trator_m),
    )

    consumo_medio_individual = calcular_cmi(rebanho.peso_medio_kg, rebanho.consumo_percent_pv)
    consumo_volumoso = calcular_cvo(consumo_medio_individual, dieta.volumoso_percent)
    consumo_materia_natural = calcular_cmn(consumo_volumoso, forragem.teor_ms_percent)
    consumo_rebanho = calcular_cr(consumo_materia_natural, rebanho.numero_animais)
    consumo_total = calcular_ct(consumo_rebanho, operacao.periodo_dias)
    volume_a_ser_ensilado = calcular_ve_t(consumo_total, forragem.perdas_percent)
    area_a_ser_plantada = calcular_ap_ha(volume_a_ser_ensilado, forragem.produtividade_mn_t_ha)
    comprimento_operacional = calcular_comprimento_operacional(
        operacao.desabastecimento_m_dia,
        operacao.periodo_dias,
    )
    volume_total_necessario = calcular_volume_total_silo(volume_a_ser_ensilado, operacao.compactacao_t_m3)
    area_minima_da_face = calcular_face_minima(
        cr_kg_dia=consumo_rebanho,
        compactacao_t_m3=operacao.compactacao_t_m3,
        desabastecimento_m_dia=operacao.desabastecimento_m_dia,
    )

    if tipo_secao == "Retangular":
        solucoes = otimizar_secao_retangular(
            volume_necessario_m3=volume_total_necessario,
            comprimento_operacional_m=comprimento_operacional,
            face_minima_m2=area_minima_da_face,
            largura_trator_m=operacao.largura_trator_m,
            altura_min_m=float(altura_min_m),
            altura_max_m=float(altura_max_m),
            passo_altura_m=float(passo_altura_m),
            passadas_min=int(passadas_min),
            passadas_max=int(passadas_max),
            folga_lateral_m=float(folga_lateral_m),
            tipo_estrutura=tipo_estrutura,
        )
    elif tipo_secao == "Trapezoidal":
        solucoes = otimizar_secao_trapezoidal(
            volume_necessario_m3=volume_total_necessario,
            comprimento_operacional_m=comprimento_operacional,
            face_minima_m2=area_minima_da_face,
            largura_trator_m=operacao.largura_trator_m,
            altura_min_m=float(altura_min_m),
            altura_max_m=float(altura_max_m),
            passo_altura_m=float(passo_altura_m),
            passadas_min=int(passadas_min),
            passadas_max=int(passadas_max),
            folga_lateral_m=float(folga_lateral_m),
            talude_h_por_v=float(talude_h_por_v),
            largura_topo_min_m=float(largura_topo_min_m),
            tipo_estrutura=tipo_estrutura,
        )
    else:
        solucoes = otimizar_secao_ovalada(
            volume_necessario_m3=volume_total_necessario,
            comprimento_operacional_m=comprimento_operacional,
            face_minima_m2=area_minima_da_face,
            largura_trator_m=operacao.largura_trator_m,
            altura_min_m=float(altura_min_m),
            altura_max_m=float(altura_max_m),
            passo_altura_m=float(passo_altura_m),
            passadas_min=int(passadas_min),
            passadas_max=int(passadas_max),
            folga_lateral_m=float(folga_lateral_m),
            largura_base_min_m=float(largura_topo_min_m),
            tipo_estrutura=tipo_estrutura,
        )

    if not solucoes:
        raise ValueError(
            "Nenhuma soluÃ§Ã£o foi encontrada com os limites informados. Ajuste altura, passadas ou talude."
        )

    melhor = solucoes[0]
    data_hora_simulacao = datetime.now().strftime("%d/%m/%Y %H:%M")
    caminho_imagem_silo = None
    caminho_logo = None

    from app.config import get_temp_dir

    pasta_temp = get_temp_dir()

    if logo_file is not None and getattr(logo_file, "name", None):
        caminho_logo = pasta_temp / logo_file.name
        with open(caminho_logo, "wb") as arquivo_logo:
            arquivo_logo.write(logo_file.getbuffer())
    dados_entrada_relatorio = {
    "Nome da propriedade ou projeto": nome_projeto,
    "Quantidade de animais": str(numero_animais),
    "Peso mÃ©dio": f"{peso_medio_kg:.2f} kg",
    "Consumo de matÃ©ria seca": f"{consumo_percent_pv:.2f} % PV",
    "ParticipaÃ§Ã£o do volumoso na dieta": f"{volumoso_percent:.2f} %",
    "Teor de matÃ©ria seca da forragem": f"{teor_ms_percent:.2f} %",
    "Perdas previstas": f"{perdas_percent:.2f} %",
    "Produtividade da forragem": f"{produtividade_mn_t_ha:.2f} t MN/ha",
    "PerÃ­odo de fornecimento": f"{periodo_dias} dias",
    "Taxa de desabastecimento": f"{desabastecimento_m_dia:.2f} m/dia",
    "CompactaÃ§Ã£o da silagem": f"{compactacao_t_m3:.2f} t MN/mÂ³",
    "Tipo estrutural do silo": tipo_estrutura,
    "Forma da seÃ§Ã£o transversal": tipo_secao,
    "Largura do trator": f"{largura_trator_m:.2f} m",
}

    resultados_relatorio = {
    "Volume a ensilar": f"{volume_a_ser_ensilado:.2f} t MN",
    "Volume do silo": f"{volume_total_necessario:.2f} mÂ³",
    "Ãrea de plantio": f"{area_a_ser_plantada:.2f} ha",
    "Comprimento operacional": f"{comprimento_operacional:.2f} m",
    "Melhor tipo de silo": melhor.tipo,
    "Base menor": f"{melhor.largura_base_m:.2f} m",
    "Base maior ou topo": f"{melhor.largura_topo_m:.2f} m",
    "Altura": f"{melhor.altura_m:.2f} m",
    "Comprimento": f"{melhor.comprimento_m:.2f} m",
    "NÃºmero de passadas": str(melhor.passadas),
}



    aba_resultado, aba_alternativas, aba_visualizacao = st.tabs(
        ["Resultado principal", "Alternativas", "VisualizaÃ§Ã£o 3D"]
    )

    with aba_resultado:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Volume a ensilar", f"{volume_a_ser_ensilado:,.2f} t MN")
        col2.metric("Volume do silo", f"{volume_total_necessario:,.2f} mÂ³")
        col3.metric("Ãrea de plantio", f"{area_a_ser_plantada:,.2f} ha")
        col4.metric("Comprimento operacional", f"{comprimento_operacional:,.2f} m")

        st.subheader("Melhor soluÃ§Ã£o encontrada")
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        c1.metric("Tipo de silo", melhor.tipo)
        c2.metric("Base menor", f"{melhor.largura_base_m:.2f} m")
        c3.metric("Base maior ou topo", f"{melhor.largura_topo_m:.2f} m")
        c4.metric("Altura", f"{melhor.altura_m:.2f} m")
        c5.metric("Comprimento", f"{melhor.comprimento_m:.2f} m")
        c6.metric("NÃºmero de passadas", str(melhor.passadas))

        st.subheader("Alertas e observaÃ§Ãµes tÃ©cnicas")
        alertas = []
        if forragem.teor_ms_percent < 28:
            alertas.append("O teor de matÃ©ria seca estÃ¡ baixo. Vale revisar o ponto de ensilagem.")
        if forragem.teor_ms_percent > 40:
            alertas.append("O teor de matÃ©ria seca estÃ¡ elevado. Isso pode dificultar a compactaÃ§Ã£o e a fermentaÃ§Ã£o.")
        if melhor.face_m2 < area_minima_da_face:
            alertas.append(
                "A melhor soluÃ§Ã£o ainda apresenta Ã¡rea da face abaixo da Ã¡rea mÃ­nima calculada para a taxa de desabastecimento informada."
            )
        if melhor.comprimento_m > 40:
            alertas.append(
                "O comprimento estÃ¡ alto. Considere ampliar a largura, a altura ou o nÃºmero de passadas aceitÃ¡veis."
            )
        if operacao.compactacao_t_m3 < 0.50:
            alertas.append("A compactaÃ§Ã£o informada estÃ¡ baixa para muitas situaÃ§Ãµes. Revise esse valor.")
        if tipo_secao == "Trapezoidal" and melhor.largura_topo_m < largura_topo_min_m:
            alertas.append("A base maior ou o topo ficaram abaixo do mÃ­nimo desejado.")

        if alertas:
            for alerta in alertas:
                st.warning(alerta)
        else:
            st.success("NÃ£o foram identificados alertas automÃ¡ticos pelos critÃ©rios atuais do modelo.")

        pdf_bytes = gerar_relatorio_pdf(
    dados_entrada=dados_entrada_relatorio,
    resultados=resultados_relatorio,
    alertas=alertas,
    nome_projeto=nome_projeto,
    data_hora_simulacao=data_hora_simulacao,
    imagem_silo_path=str(caminho_imagem_silo) if caminho_imagem_silo is not None else None,
    logo_path=str(caminho_logo) if caminho_logo is not None else None,
    responsavel_tecnico=responsavel_tecnico if responsavel_tecnico else None,
)


        

        st.download_button(
            label="Baixar relatÃ³rio em PDF",
            data=pdf_bytes,
            file_name="relatorio_dimensionamento_silo.pdf",
            mime="application/pdf",
        )

    with aba_alternativas:
        st.subheader("Top 10 soluÃ§Ãµes")
        tabela_solucoes = pd.DataFrame(
            [
                {
                    "Tipo de silo": s.tipo,
                    "Base menor (m)": s.largura_base_m,
                    "Base maior ou topo (m)": s.largura_topo_m,
                    "Altura (m)": s.altura_m,
                    "Comprimento (m)": s.comprimento_m,
                    "Ãrea da seÃ§Ã£o transversal (mÂ²)": s.area_secao_m2,
                    "Ãrea da face (mÂ²)": s.face_m2,
                    "Volume do silo (mÂ³)": s.volume_silo_m3,
                    "Excedente de volume (mÂ³)": s.excedente_m3,
                    "NÃºmero de passadas": s.passadas,
                    "PontuaÃ§Ã£o da otimizaÃ§Ã£o": s.penalidade,
                }
                for s in solucoes[:10]
            ]
        )
        st.dataframe(tabela_solucoes, use_container_width=True, hide_index=True)

    with aba_visualizacao:
        st.subheader("VisualizaÃ§Ã£o tridimensional da melhor soluÃ§Ã£o")
        if "Ovalada" in melhor.tipo:
            figura = go.Figure(
                data=[
                    criar_solido_superficie_oval(
                        melhor.largura_base_m,
                        melhor.altura_m,
                        melhor.comprimento_m,
                    )
                ]
            )
        else:
            figura = go.Figure(
                data=[
                    criar_solido_prismatico(
                        melhor.largura_base_m,
                        melhor.largura_topo_m,
                        melhor.altura_m,
                        melhor.comprimento_m,
                    )
                ]
            )

        figura.update_layout(
            scene=dict(
                xaxis_title="Largura (m)",
                yaxis_title="Comprimento (m)",
                zaxis_title="Altura (m)",
                aspectmode="data",
            ),
            margin=dict(l=0, r=0, t=30, b=0),
        )
        st.plotly_chart(figura, use_container_width=True)

        try:
            from app.config import get_temp_dir

            pasta_imagens = get_temp_dir()
            caminho_imagem_silo = pasta_imagens / "visualizacao_silo.png"
            figura.write_image(str(caminho_imagem_silo), width=1200, height=700)
        except Exception:
            caminho_imagem_silo = None
except Exception as erro:
    st.error(f"Erro no cÃ¡lculo: {erro}")    

