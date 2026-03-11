#!/usr/bin/env python3
"""能力评估器"""

import json
from pathlib import Path
from datetime import datetime

EXPERIENCE_DB = Path.home() / '.openclaw' / 'workspace' / 'data' / 'experiences.json'

def assess_capabilities(days=7):
    """评估过去 N 天的能力水平"""
    
    if not EXPERIENCE_DB.exists():
        return {"error": "No experience data found"}
    
    with open(EXPERIENCE_DB, 'r', encoding='utf-8') as f:
        experiences = json.load(f)
    
    # 过滤最近 N 天的经验
    cutoff = datetime.now().timestamp() - (days * 24 * 3600)
    recent = [e for e in experiences if e.get('timestamp', 0) > cutoff]
    
    if not recent:
        return {"error": "No recent experience data"}
    
    # 按能力维度统计
    capabilities = {
        'code_generation': {'success': 0, 'total': 0, 'quality_sum': 0},
        'error_handling': {'success': 0, 'total': 0, 'quality_sum': 0},
        'optimization': {'success': 0, 'total': 0, 'quality_sum': 0},
        'learning': {'success': 0, 'total': 0, 'quality_sum': 0}
    }
    
    for exp in recent:
        task_type = exp.get('task', 'unknown')
        outcome = exp.get('outcome', 'failure')
        quality = exp.get('metrics', {}).get('quality_score', 0.5)
        
        # 简单分类
        if 'code' in task_type or 'script' in task_type:
            cap = 'code_generation'
        elif 'error' in task_type:
            cap = 'error_handling'
        elif 'optim' in task_type:
            cap = 'optimization'
        else:
            cap = 'learning'
        
        capabilities[cap]['total'] += 1
        if outcome == 'success':
            capabilities[cap]['success'] += 1
        capabilities[cap]['quality_sum'] += quality
    
    # 计算得分
    assessment = {
        'overall_score': 0,
        'capabilities': {},
        'weaknesses': [],
        'strengths': [],
        'assessed_at': datetime.now().isoformat(),
        'period_days': days,
        'total_experiences': len(recent)
    }
    
    scores = []
    for cap, data in capabilities.items():
        if data['total'] > 0:
            success_rate = data['success'] / data['total']
            avg_quality = data['quality_sum'] / data['total']
            score = int((success_rate * 0.6 + avg_quality * 0.4) * 100)
        else:
            score = 50  # 默认分
        
        capabilities[cap] = score
        scores.append(score)
        
        if score < 70:
            assessment['weaknesses'].append(cap)
        elif score > 85:
            assessment['strengths'].append(cap)
    
    assessment['overall_score'] = int(sum(scores) / len(scores)) if scores else 0
    assessment['capabilities'] = capabilities
    
    return assessment

def save_assessment(assessment):
    """保存评估结果"""
    output_dir = Path.home() / '.openclaw' / 'workspace' / 'data' / 'assessments'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = output_dir / f'assessment_{timestamp}.json'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(assessment, f, indent=2, ensure_ascii=False)
    
    return str(output_file)

if __name__ == "__main__":
    assessment = assess_capabilities(days=7)
    print(json.dumps(assessment, indent=2, ensure_ascii=False))
    
    output_file = save_assessment(assessment)
    print(f"\n评估报告已保存到：{output_file}")
