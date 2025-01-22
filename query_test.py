from db2 import DB2Connection
import os


def main():
    query_str = '''
    select
        CAA.ID_PESSOA, CAA.ID_CURSO, strip(upper(CAA.MATRICULA)) MATRICULA, 
        CASE
            WHEN VERSOES.ID_VERSAO_CURSO IS NULL THEN 1
            ELSE VERSOES.ID_VERSAO_CURSO
        END AS ID_VERSAO_CURSO,
        di.MENOR_ANO_INGRESSO ANO_INGRESSO, di.maior_ano_evasao ANO_EVASAO, 
        ((CA.ANO - di.MENOR_ANO_INGRESSO) + 1) ANO_CURSO,
        strip(CAA.FORMA_EVASAO) FORMA_EVASAO, CA.ANO ANO_TURMA, DISCI.ID_DISCIPLINA,
        FLOAT(CA.MEDIA_FINAL) MEDIA_FINAL, FLOAT(CA.CH_TOTAL) CH_TOTAL,
        VDBC.CARGA_HORARIA_CURSO, VDBC.QUANTIDADE_DISCIPLINAS_CURRICULO_BASICO
    from CURRICULO_ALUNO ca
    inner join CURSOS_ALUNOS_ATZ caa on ca.ID_CURSO_ALUNO = caa.ID_CURSO_ALUNO
    inner join CURSOS on caa.ID_CURSO = cursos.ID_CURSO
    inner join ACAD_CURSOS ac on cursos.ID_CURSO = ac.ID_CURSO
    inner join ACAD_MODALIDADE am on ac.ID_MODALIDADE = am.ID_MODALIDADE
    inner join ACAD_CLASSIFICACAO acla on ac.ID_CLASSIF = acla.ID_CLASSIF
    inner join ACAD_NIVEL_CURSOS anc on ac.id_nivel = anc.id_nivel
    left join bee.VERSOES_CURSOS versoes
        ON cursos.ID_CURSO = versoes.ID_CURSO AND cursos.ID_VERSAO_CORRENTE = versoes.ID_VERSAO_CURSO
    inner join bee.V_DISCIPLINAS disci ON disci.ID_DISCIPLINA = ca.ID_ATIV_CURRIC
    inner join TAB_ESTRUTURADA tipo_disci
        on disci.TIPO_DISC_TAB = tipo_disci.COD_TABELA and disci.TIPO_DISC_ITEM = tipo_disci.ITEM_TABELA
    left join V_DISCIPLINAS_BASICAS_CURSO vdbc on caa.ID_CURSO = vdbc.ID_CURSO
    inner join (
        select
            matricula,
            min(ano_ingresso) as MENOR_ANO_INGRESSO,
            max(ano_evasao) as MAIOR_ANO_EVASAO
        from CURSOS_ALUNOS_ATZ
        group by matricula
    ) AS DI on caa.MATRICULA = DI.MATRICULA
    WHERE (
        (DI.MENOR_ANO_INGRESSO >= 2015) AND
        (DI.MENOR_ANO_INGRESSO <= 2018) AND
        (ca.SITUACAO_OCOR <> 'E') AND -- remove turmas excluídas
        -- ((ca.MEDIA_FINAL IS NOT NULL) OR (ca.ANO = YEAR(CURRENT_DATE))) AND -- turmas concluídas ou abertas no ano corrente
        (ca.ID_TURMA IS NOT NULL) AND (
            (upper(strip(am.DESCRICAO)) LIKE '%ENSINO MÉDIO%') OR
            (upper(strip(am.DESCRICAO)) LIKE '%TÉCNICO%')
        ) AND (
            (UPPER(STRIP(acla.DESCRICAO)) = 'PRESENCIAL') OR
            (UPPER(STRIP(acla.DESCRICAO)) = 'EAD')
        )
    );
    '''
    
    with DB2Connection(os.path.join('instance', 'database_credentials.json')) as conn:
        df = conn.query_to_dataframe(query_str)

if __name__ == '__main__':
    main()
