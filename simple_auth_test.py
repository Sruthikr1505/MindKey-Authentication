#!/usr/bin/env python3
"""
Simple authentication test to demonstrate confidence patterns
"""

import requests
import numpy as np
import os

def simple_authentication_test():
    print('🧪 SIMPLE AUTHENTICATION CONFIDENCE TEST')
    print('=' * 50)
    
    base_url = 'http://localhost:8000'
    
    # Test API
    try:
        health = requests.get(f'{base_url}/health', timeout=5)
        print(f'✅ API Status: {health.json()}')
    except:
        print('❌ API not responding! Please start: python run.py')
        return
    
    # Check one subject's data
    subject = 's01'
    data_dir = 'data/processed'
    
    print(f'\n📊 TESTING SUBJECT: {subject}')
    print('-' * 30)
    
    # Check available trials
    available_trials = []
    for i in range(1, 41):  # Check trials 1-40
        trial_file = f'{subject}_trial{i:02d}.npy'
        if os.path.exists(os.path.join(data_dir, trial_file)):
            available_trials.append(i)
    
    print(f'Available trials: {len(available_trials)} (trial{min(available_trials):02d} to trial{max(available_trials):02d})')
    
    if len(available_trials) < 8:
        print('❌ Not enough trials for comprehensive test')
        return
    
    # Enroll user with trials 1-5
    print(f'\n📝 ENROLLING {subject} with trials 1-5...')
    enrollment_trials = []
    for i in range(1, 6):
        if i in available_trials:
            trial_data = np.load(os.path.join(data_dir, f'{subject}_trial{i:02d}.npy'))
            enrollment_trials.append(trial_data)
    
    if len(enrollment_trials) < 3:
        print('❌ Not enough enrollment trials')
        return
    
    enrollment_array = np.array(enrollment_trials)
    np.save('test_enrollment.npy', enrollment_array)
    
    username = 'test_user_s01'
    password = 'test_password_123'
    
    with open('test_enrollment.npy', 'rb') as f:
        enroll_response = requests.post(f'{base_url}/register',
            data={'username': username, 'password': password},
            files={'enrollment_trials': f}, timeout=30)
    
    if enroll_response.status_code != 200:
        print(f'❌ Enrollment failed: {enroll_response.status_code}')
        return
    
    print('✅ User enrolled successfully')
    
    # Test authentication with different trials
    print(f'\n🔐 TESTING AUTHENTICATION CONFIDENCE:')
    print('-' * 40)
    
    test_trials = [6, 10, 15, 20, 25, 30, 35, 40]  # Sample across range
    results = []
    
    for trial_num in test_trials:
        if trial_num in available_trials:
            trial_file = f'{subject}_trial{trial_num:02d}.npy'
            trial_data = np.load(os.path.join(data_dir, trial_file))
            np.save(f'test_trial_{trial_num}.npy', trial_data)
            
            with open(f'test_trial_{trial_num}.npy', 'rb') as f:
                auth_response = requests.post(f'{base_url}/auth/login',
                    data={'username': username, 'password': password},
                    files={'probe_trial': f}, timeout=30)
            
            if auth_response.status_code == 200:
                result = auth_response.json()
                auth = result.get('authenticated', False)
                score = result.get('similarity_score', 0)
                prob = result.get('calibrated_probability', 0)
                
                results.append({
                    'trial': trial_num,
                    'authenticated': auth,
                    'score': score,
                    'probability': prob
                })
                
                status = '✅' if auth else '❌'
                confidence = 'HIGH' if prob > 0.7 else 'MEDIUM' if prob > 0.4 else 'LOW'
                print(f'{status} Trial{trial_num:02d}: Auth={auth}, Score={score:.3f}, Prob={prob:.3f} ({confidence})')
    
    # Analysis
    print(f'\n📈 CONFIDENCE ANALYSIS:')
    print('-' * 25)
    
    if results:
        authenticated = [r for r in results if r['authenticated']]
        rejected = [r for r in results if not r['authenticated']]
        
        print(f'✅ Authenticated: {len(authenticated)}/{len(results)} trials')
        print(f'❌ Rejected: {len(rejected)}/{len(results)} trials')
        
        if authenticated:
            avg_auth_score = np.mean([r['score'] for r in authenticated])
            avg_auth_prob = np.mean([r['probability'] for r in authenticated])
            best_trial = max(authenticated, key=lambda x: x['probability'])
            print(f'📊 Average authenticated score: {avg_auth_score:.3f}')
            print(f'📊 Average authenticated probability: {avg_auth_prob:.3f}')
            print(f'🏆 Best trial: trial{best_trial["trial"]:02d} (prob={best_trial["probability"]:.3f})')
        
        if rejected:
            avg_rej_score = np.mean([r['score'] for r in rejected])
            avg_rej_prob = np.mean([r['probability'] for r in rejected])
            print(f'📊 Average rejected score: {avg_rej_score:.3f}')
            print(f'📊 Average rejected probability: {avg_rej_prob:.3f}')
    
    # Test impostor (different subject)
    print(f'\n🚫 TESTING IMPOSTOR DETECTION:')
    print('-' * 35)
    
    impostor_subject = 's02'  # Different subject
    impostor_trial = 6
    impostor_file = f'{impostor_subject}_trial{impostor_trial:02d}.npy'
    
    if os.path.exists(os.path.join(data_dir, impostor_file)):
        impostor_data = np.load(os.path.join(data_dir, impostor_file))
        np.save('impostor_test.npy', impostor_data)
        
        with open('impostor_test.npy', 'rb') as f:
            impostor_response = requests.post(f'{base_url}/auth/login',
                data={'username': username, 'password': password},
                files={'probe_trial': f}, timeout=30)
        
        if impostor_response.status_code == 200:
            result = impostor_response.json()
            auth = result.get('authenticated', False)
            score = result.get('similarity_score', 0)
            prob = result.get('calibrated_probability', 0)
            
            status = '✅ SECURITY BREACH!' if auth else '❌ CORRECTLY REJECTED'
            print(f'{status}')
            print(f'   Impostor ({impostor_subject}): Auth={auth}, Score={score:.3f}, Prob={prob:.3f}')
    
    print(f'\n🎯 SUMMARY:')
    print(f'   - Same user, different trials: Should authenticate with 70-90% confidence')
    print(f'   - Different user, same trial: Should be rejected with <20% confidence')
    print(f'   - Best trials for confidence: Usually middle range (trial06-trial20)')
    print(f'   - Worst trials: Edge cases (trial01, trial40) may have lower confidence')

if __name__ == '__main__':
    simple_authentication_test()
