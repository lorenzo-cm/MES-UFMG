"""
Script para analisar e comparar os resultados da LLM vs SonarQube.
"""
import json
from pathlib import Path
from collections import defaultdict


def analyze_dataset(dataset_path: str):
    """Analisa um arquivo de dataset e compara LLM vs SonarQube."""
    
    data = json.loads(Path(dataset_path).read_text())
    
    print("=" * 80)
    print(f"ANÁLISE DO PR #{data['pr_number']}")
    print("=" * 80)
    print(f"Autor: {data['pr_author']}")
    print(f"Data: {data['created_at']}")
    print(f"Ground Truth: {data.get('ground_truth_smells', [])}")
    
    llm_smells = data.get('llm_smells', [])
    sonar_issues = data.get('sonar_issues', [])
    
    print(f"\n📊 Total de smells detectados:")
    print(f"  LLM: {len(llm_smells)}")
    print(f"  SonarQube: {len(sonar_issues)}")
    
    # Análise por arquivo
    llm_by_file = defaultdict(list)
    sonar_by_file = defaultdict(list)
    
    for smell in llm_smells:
        llm_by_file[smell['file']].append(smell)
    
    for issue in sonar_issues:
        # Extrai o path do componente
        component = issue.get('component', '')
        file_path = component.split(':', 1)[-1] if ':' in component else ''
        sonar_by_file[file_path].append(issue)
    
    # Comparação por arquivo
    all_files = set(llm_by_file.keys()) | set(sonar_by_file.keys())
    
    if all_files:
        print("\n" + "=" * 80)
        print("COMPARAÇÃO POR ARQUIVO:")
        print("=" * 80)
        
        for file in sorted(all_files):
            llm_count = len(llm_by_file[file])
            sonar_count = len(sonar_by_file[file])
            
            print(f"\n📁 {file}")
            print(f"  LLM: {llm_count} smell(s)")
            print(f"  SonarQube: {sonar_count} issue(s)")
            
            # Mostra detalhes LLM
            if llm_by_file[file]:
                print("\n  🤖 LLM detectou:")
                for smell in llm_by_file[file]:
                    print(f"    - L{smell['line']}: {smell['smell_type']} ({smell['severity']})")
                    print(f"      {smell['message'][:80]}...")
            
            # Mostra detalhes SonarQube
            if sonar_by_file[file]:
                print("\n  🔍 SonarQube detectou:")
                for issue in sonar_by_file[file]:
                    print(f"    - L{issue['line']}: {issue['rule']} ({issue['severity']})")
                    print(f"      {issue['message'][:80]}...")
    
    # Análise de sobreposição (mesma linha)
    print("\n" + "=" * 80)
    print("ANÁLISE DE SOBREPOSIÇÃO:")
    print("=" * 80)
    
    # Cria mapa de linhas
    llm_lines = {(smell['file'], smell['line']) for smell in llm_smells}
    sonar_lines = {
        (issue.get('component', '').split(':', 1)[-1], issue.get('line'))
        for issue in sonar_issues
    }
    
    overlap = llm_lines & sonar_lines
    llm_only = llm_lines - sonar_lines
    sonar_only = sonar_lines - llm_lines
    
    print(f"\n✅ Detectados por ambos: {len(overlap)} localizações")
    if overlap:
        for file, line in sorted(overlap):
            print(f"  - {file}:{line}")
    
    print(f"\n🤖 Detectados apenas pela LLM: {len(llm_only)} localizações")
    if llm_only:
        for file, line in sorted(llm_only):
            print(f"  - {file}:{line}")
    
    print(f"\n🔍 Detectados apenas pelo SonarQube: {len(sonar_only)} localizações")
    if sonar_only:
        for file, line in sorted(sonar_only):
            print(f"  - {file}:{line}")
    
    # Estatísticas de tipos
    print("\n" + "=" * 80)
    print("TIPOS DE SMELLS (LLM):")
    print("=" * 80)
    
    smell_types = defaultdict(int)
    severity_count = defaultdict(int)
    
    for smell in llm_smells:
        smell_types[smell['smell_type']] += 1
        severity_count[smell['severity']] += 1
    
    for smell_type, count in sorted(smell_types.items(), key=lambda x: x[1], reverse=True):
        print(f"  {smell_type}: {count}")
    
    print(f"\n📊 Por severidade:")
    for severity, count in sorted(severity_count.items()):
        print(f"  {severity}: {count}")
    
    print("\n" + "=" * 80)


def compare_multiple_datasets(dataset_dir: str = "dataset-pr-6"):
    """Compara múltiplos datasets."""
    dataset_path = Path(dataset_dir)
    
    if not dataset_path.exists():
        print(f"❌ Diretório {dataset_dir} não encontrado")
        return
    
    json_files = list(dataset_path.glob("pr_*.json"))
    
    if not json_files:
        print(f"❌ Nenhum arquivo de dataset encontrado em {dataset_dir}")
        return
    
    print(f"📂 Analisando {len(json_files)} dataset(s)...\n")
    
    for json_file in sorted(json_files):
        analyze_dataset(str(json_file))
        print("\n")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Analisa arquivo específico
        analyze_dataset(sys.argv[1])
    else:
        # Analisa todos os datasets
        compare_multiple_datasets()
