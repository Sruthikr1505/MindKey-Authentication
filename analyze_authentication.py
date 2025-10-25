#!/usr/bin/env python3
"""
Comprehensive authentication analysis for EEG trials
Tests different scenarios and identifies high-confidence patterns
"""

import requests
import numpy as np
import json
import os
import time
from itertools import combinations

def test_authentication_scenarios():
    print('🧪 COMPREHENSIVE AUTHENTICATION ANALYSIS')
    print('=' * 60)
    
    base_url = 'http://localhost:8000'
    
    # Test API connectivity
    try:
        health = requests.get(f'{base_url}/health', timeout=5)
        print(f'✅ API Status: {health.json()}')
    except:
        print('❌ API not responding! Start API first: python run.py')
        return
    
    # Check available data
    data_dir = 'data/processed'
    if not os.path.exists(data_dir):
        print('❌ No processed data found!')
        return
    
    # Get all trial files
    trial_files = {}
    for file in os.listdir(data_dir):
        if file.endswith('.npy') and 's' in file and 'trial' in file:
            parts = file.replace('.npy', '').split('_')
            if len(parts) >= 2:
                subject = parts[0]  # s01, s02, etc.
                trial = parts[1]    # trial01, trial02, etc.
                if subject not in trial_files:
                    trial_files[subject] = []
                trial_files[subject].append(trial)
    
    print(f'📁 Found data for {len(trial_files)} subjects')
    for subject, trials in trial_files.items():
        print(f'   {subject}: {len(trials)} trials')
    
    # Analysis scenarios
    scenarios = {
        'same_user_different_trials': [],
        'different_users_same_trial': [],
        'different_users_different_trials': [],
        'high_confidence_genuine': [],
        'high_confidence_impostor': []
    }
    
    print('\n🔬 SCENARIO 1: SAME USER, DIFFERENT TRIALS')
    print('-' * 50)
    
    # Test same user with different trials
    for subject in list(trial_files.keys())[:3]:  # Test first 3 subjects
        if len(trial_files[subject]) >= 3:
            print(f'\n👤 Testing {subject}...')
            
            # Use trial01 for enrollment, test with trial06-08
            enrollment_trials = []
            for t in range(1, 6):  # trials 1-5 for enrollment
                trial_file = f'{subject}_trial{t:02d}.npy'
                if os.path.exists(os.path.join(data_dir, trial_file)):
                    trial_data = np.load(os.path.join(data_dir, trial_file))
                    enrollment_trials.append(trial_data)
            
            if len(enrollment_trials) >= 3:
                # Enroll user
                enrollment_array = np.array(enrollment_trials)
                np.save(f'temp_enroll_{subject}.npy', enrollment_array)
                
                username = f'test_{subject}'
                password = f'pass_{subject}'
                
                with open(f'temp_enroll_{subject}.npy', 'rb') as f:
                    enroll_response = requests.post(f'{base_url}/register',
                        data={'username': username, 'password': password},
                        files={'enrollment_trials': f}, timeout=30)
                
                if enroll_response.status_code == 200:
                    print(f'   ✅ Enrolled {username}')
                    
                    # Test with different trials (6-10)
                    for test_trial in range(6, 11):
                        trial_file = f'{subject}_trial{test_trial:02d}.npy'
                        trial_path = os.path.join(data_dir, trial_file)
                        
                        if os.path.exists(trial_path):
                            trial_data = np.load(trial_path)
                            np.save(f'temp_test_{subject}_{test_trial}.npy', trial_data)
                            
                            with open(f'temp_test_{subject}_{test_trial}.npy', 'rb') as f:
                                auth_response = requests.post(f'{base_url}/auth/login',
                                    data={'username': username, 'password': password},
                                    files={'probe_trial': f}, timeout=30)
                            
                            if auth_response.status_code == 200:
                                result = auth_response.json()
                                auth = result.get('authenticated', False)
                                score = result.get('similarity_score', 0)
                                prob = result.get('calibrated_probability', 0)
                                
                                scenarios['same_user_different_trials'].append({
                                    'subject': subject,
                                    'trial': f'trial{test_trial:02d}',
                                    'authenticated': auth,
                                    'score': score,
                                    'probability': prob
                                })
                                
                                status = '✅' if auth else '❌'
                                print(f'   {status} Trial{test_trial:02d}: Auth={auth}, Score={score:.3f}, Prob={prob:.3f}')
                                
                                # Track high confidence results
                                if auth and prob > 0.9:
                                    scenarios['high_confidence_genuine'].append({
                                        'subject': subject,
                                        'trial': f'trial{test_trial:02d}',
                                        'score': score,
                                        'probability': prob
                                    })
    
    print('\n🔬 SCENARIO 2: DIFFERENT USERS, SAME TRIAL')
    print('-' * 50)
    
    # Test different users with same trial number
    test_trial_num = 6  # Use trial06 for testing
    enrolled_users = []
    
    # First enroll multiple users
    for subject in list(trial_files.keys())[:5]:  # Test 5 subjects
        enrollment_trials = []
        for t in range(1, 6):
            trial_file = f'{subject}_trial{t:02d}.npy'
            if os.path.exists(os.path.join(data_dir, trial_file)):
                trial_data = np.load(os.path.join(data_dir, trial_file))
                enrollment_trials.append(trial_data)
        
        if len(enrollment_trials) >= 3:
            enrollment_array = np.array(enrollment_trials)
            np.save(f'multi_enroll_{subject}.npy', enrollment_array)
            
            username = f'multi_{subject}'
            password = f'multi_pass_{subject}'
            
            with open(f'multi_enroll_{subject}.npy', 'rb') as f:
                enroll_response = requests.post(f'{base_url}/register',
                    data={'username': username, 'password': password},
                    files={'enrollment_trials': f}, timeout=30)
            
            if enroll_response.status_code == 200:
                enrolled_users.append({'subject': subject, 'username': username, 'password': password})
    
    # Now test each user with trial06 from different subjects
    for user in enrolled_users:
        print(f'\n👤 Testing {user["username"]} with different subjects trial06...')
        
        for test_subject in list(trial_files.keys())[:5]:
            trial_file = f'{test_subject}_trial{test_trial_num:02d}.npy'
            trial_path = os.path.join(data_dir, trial_file)
            
            if os.path.exists(trial_path):
                trial_data = np.load(trial_path)
                np.save(f'cross_test_{user["subject"]}_{test_subject}.npy', trial_data)
                
                with open(f'cross_test_{user["subject"]}_{test_subject}.npy', 'rb') as f:
                    auth_response = requests.post(f'{base_url}/auth/login',
                        data={'username': user['username'], 'password': user['password']},
                        files={'probe_trial': f}, timeout=30)
                
                if auth_response.status_code == 200:
                    result = auth_response.json()
                    auth = result.get('authenticated', False)
                    score = result.get('similarity_score', 0)
                    prob = result.get('calibrated_probability', 0)
                    
                    is_same_user = user['subject'] == test_subject
                    scenario_type = 'different_users_same_trial' if not is_same_user else 'same_user_different_trials'
                    
                    scenarios[scenario_type].append({
                        'enrolled_user': user['subject'],
                        'test_subject': test_subject,
                        'trial': f'trial{test_trial_num:02d}',
                        'authenticated': auth,
                        'score': score,
                        'probability': prob,
                        'is_genuine': is_same_user
                    })
                    
                    status = '✅' if auth else '❌'
                    user_type = 'GENUINE' if is_same_user else 'IMPOSTOR'
                    print(f'   {status} {test_subject} ({user_type}): Auth={auth}, Score={score:.3f}, Prob={prob:.3f}')
                    
                    # Track high confidence impostors (should be rejected)
                    if not is_same_user and not auth and prob < 0.1:
                        scenarios['high_confidence_impostor'].append({
                            'enrolled_user': user['subject'],
                            'impostor_subject': test_subject,
                            'trial': f'trial{test_trial_num:02d}',
                            'score': score,
                            'probability': prob
                        })
    
    # Analysis Summary
    print('\n📊 AUTHENTICATION ANALYSIS SUMMARY')
    print('=' * 60)
    
    # Same user, different trials
    same_user_results = scenarios['same_user_different_trials']
    if same_user_results:
        genuine_auths = [r for r in same_user_results if r['authenticated']]
        genuine_rate = len(genuine_auths) / len(same_user_results) * 100
        avg_genuine_score = np.mean([r['score'] for r in genuine_auths]) if genuine_auths else 0
        print(f'\n🔹 SAME USER, DIFFERENT TRIALS:')
        print(f'   Genuine Authentication Rate: {genuine_rate:.1f}% ({len(genuine_auths)}/{len(same_user_results)})')
        print(f'   Average Genuine Score: {avg_genuine_score:.3f}')
    
    # Different users, same trial
    diff_user_results = scenarios['different_users_same_trial']
    if diff_user_results:
        impostor_auths = [r for r in diff_user_results if r['authenticated'] and not r['is_genuine']]
        impostor_rate = len(impostor_auths) / len([r for r in diff_user_results if not r['is_genuine']]) * 100 if diff_user_results else 0
        print(f'\n🔹 DIFFERENT USERS, SAME TRIAL:')
        print(f'   Impostor Authentication Rate: {impostor_rate:.1f}% (should be 0%)')
        print(f'   False Acceptance Rate: {impostor_rate:.1f}%')
    
    # High confidence results
    high_conf_genuine = scenarios['high_confidence_genuine']
    high_conf_impostor = scenarios['high_confidence_impostor']
    
    print(f'\n🔹 HIGH CONFIDENCE RESULTS:')
    print(f'   100% Confidence Genuine: {len(high_conf_genuine)} cases')
    for case in high_conf_genuine[:5]:  # Show top 5
        print(f'     {case["subject"]} {case["trial"]}: Score={case["score"]:.3f}, Prob={case["probability"]:.3f}')
    
    print(f'   100% Confidence Impostor: {len(high_conf_impostor)} cases')
    for case in high_conf_impostor[:5]:  # Show top 5
        print(f'     {case["enrolled_user"]} vs {case["impostor_subject"]}: Score={case["score"]:.3f}, Prob={case["probability"]:.3f}')
    
    # Save detailed results
    with open('authentication_analysis.json', 'w') as f:
        json.dump(scenarios, f, indent=2)
    
    print(f'\n💾 Detailed results saved to authentication_analysis.json')
    
    # Recommendations
    print(f'\n🎯 RECOMMENDATIONS:')
    if genuine_rate < 80:
        print('   ⚠️  Low genuine authentication rate - consider model retraining')
    if impostor_rate > 10:
        print('   ⚠️  High impostor acceptance rate - strengthen authentication threshold')
    
    print('\n✅ Analysis complete!')

if __name__ == '__main__':
    test_authentication_scenarios()
