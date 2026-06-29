import pandas as pd
import datetime as dt
import ast

def calc_rt(start, rt, diff, i) :    
    rt = dt.datetime.strptime(rt, '%H:%M:%S')
    rt_act = rt - (start + dt.timedelta(0,(diff.total_seconds()/6)*i))
    return rt_act.total_seconds()

def check_correct(director, guessor, inputs, rts, start, diff) :
    #see when guessor image occurs in director list, then compare to answer in box
    graded_set = []
    #get accuracy % and round rt
    round_accuracy = 0
    round_rt = 0
    for i, d in enumerate(director) :
        accurate = False
        correct_indices = []
        correct_rt = []
        all_incorrect_responses = []
        all_incorrect_rt = []
        num_responses = 0
        for j, g, in enumerate(guessor) :
            incorrect_indices = []
            incorrect_responses = []
            incorrect_rt = []
            inp = ast.literal_eval(inputs[j])
            if str(i+1) in inp :
                if d == g :      
                    correct_indices = [k for k, x in enumerate(inp) if x == str(i+1)]    
                    incorrect_responses = [x for x in inp if x != str(i+1)]
                    num_responses = len(inp)       
                    crt_set = [ast.literal_eval(rts[j])[k] for k in correct_indices]
                    for rt in crt_set :
                        correct_rt.append(calc_rt(start, rt, diff, i))                                     
                    if correct_indices[-1] == len(inp)-1 :
                        accurate = True
                else :
                    incorrect_indices = [k for k, x in enumerate(inp) if x == str(i+1)]    
                    irt_set = [ast.literal_eval(rts[j])[k] for k in incorrect_indices]
                    for ind, rt in zip(incorrect_indices, irt_set) :
                        incorrect_rt.append(calc_rt(start, rt, diff, ind))
            else :
                if d == g :
                    num_responses = len(inp)
                    incorrect_responses = inp
            [all_incorrect_rt.append(x) for x in incorrect_rt]    
            [all_incorrect_responses.append(x) for x in incorrect_responses]        
        if accurate :
            round_accuracy += 1
            if correct_rt[::-1][0] <= 20 :
                round_rt += correct_rt[::-1][0]
            else :
                round_rt += 20
        else :
            round_rt += 20
        
        graded = {'image': d, 'correct?': accurate, 'correct rt': correct_rt, 'incorrect rt': all_incorrect_rt,
                  'incorrect resp box': all_incorrect_responses, 'number resp box': num_responses}
        graded_set.append(graded)     
    return round_accuracy/6, round_rt, graded_set 

pl1_file = pd.read_csv('/Users/mizwally/Desktop/DYAD_01-tangrams/DYAD_01_SCAN_011_abstract-images.csv')
pl2_file = pd.read_csv('/Users/mizwally/Desktop/DYAD_01-tangrams/DYAD_01_SCAN_012_abstract-images.csv')
#pl1_file = pd.read_csv('C:\\Users\\mizwa\\Downloads\\DYAD_01_SCAN_011_abstract-images.csv')
#pl2_file = pd.read_csv('C:\\Users\\mizwa\\Downloads\\DYAD_01_SCAN_012_abstract-images.csv')
pl1_director = pl1_file[pl1_file['Role'] == 'director']
pl1_guessor = pl1_file[pl1_file['Role'] == 'guessor']
pl2_director = pl2_file[pl2_file['Role'] == 'director']
pl2_guessor = pl2_file[pl2_file['Role'] == 'guessor']

pl1_rounds = []
pl2_rounds = []
for i in range(len(pl2_director.index)):
    round = {'director': list(pl2_director.iloc[i][9:15]), 
             'guessor': list(pl1_guessor.iloc[i][9:15]), 
             'inputs': list(pl1_guessor.iloc[i][15:27:2]),
             'rts': list(pl1_guessor.iloc[i][16:28:2]),
             'start_time': pl2_director.iloc[i]['Round_start_time'],
             'end_time': pl2_director.iloc[i]['Round_end_time'],
             'control': pl1_guessor.iloc[i]['Control?']}
    pl1_rounds.append(round)
for i in range(len(pl1_director.index)):
    round = {'director': list(pl1_director.iloc[i][9:15]), 
             'guessor': list(pl2_guessor.iloc[i][9:15]), 
             'inputs': list(pl2_guessor.iloc[i][15:27:2]),
             'rts': list(pl2_guessor.iloc[i][16:28:2]),
             'start_time': pl1_director.iloc[i]['Round_start_time'],
             'end_time': pl1_director.iloc[i]['Round_end_time'],
             'control': pl2_guessor.iloc[i]['Control?']}
    pl2_rounds.append(round)

pl1_answers = []
pl1_accs = []
pl1_rts = []
pl2_answers = []
pl2_accs = []
pl2_rts = []
for i in range(len(pl1_rounds)) :
    pl1_st = dt.datetime.strptime(pl1_rounds[i]['start_time'], '%H:%M:%S')
    pl1_end = dt.datetime.strptime(pl1_rounds[i]['end_time'], '%H:%M:%S')
    pl1_diff = pl1_end - pl1_st
    if pl1_rounds[i]['control'] == False :
        pl1_acc, pl1_rt, pl1_ans = check_correct(pl1_rounds[i]['director'], pl1_rounds[i]['guessor'], pl1_rounds[i]['inputs'], 
                                pl1_rounds[i]['rts'], pl1_st, pl1_diff)
        pl1_answers.append(pl1_ans)
        pl1_accs.append(pl1_acc)
        pl1_rts.append(pl1_rt)
    else :
        pl1_answers.append(['control'])
        pl1_accs.append('N/A')
        pl1_rts.append('N/A')

    pl2_st = dt.datetime.strptime(pl2_rounds[i]['start_time'], '%H:%M:%S')
    pl2_end = dt.datetime.strptime(pl2_rounds[i]['end_time'], '%H:%M:%S')
    pl2_diff = pl2_end - pl2_st 
    if pl2_rounds[i]['control'] == False :
        pl2_acc, pl2_rt, pl2_ans = check_correct(pl2_rounds[i]['director'], pl2_rounds[i]['guessor'], pl2_rounds[i]['inputs'], 
                                pl2_rounds[i]['rts'], pl2_st, pl2_diff)
        pl2_answers.append(pl2_ans)
        pl2_accs.append(pl2_acc)
        pl2_rts.append(pl2_rt)
    else :
        pl2_answers.append(['control'])
        pl2_accs.append('N/A')
        pl2_rts.append('N/A')

pl1_answer_file = pd.concat([pl1_guessor[pl1_guessor.columns[:5]].reset_index(drop=True), pd.Series(pl1_accs, name='Accuracy'), 
                             pd.Series(pl1_rts, name='RT'), pd.DataFrame(pl1_answers)], axis=1).drop(columns=['Role', 'Control?'])
pl1_answer_file.to_csv('/Users/mizwally/Desktop/DYAD_01-tangrams/DYAD_01_SCAN_011_answers.csv', index=False)
pl2_answer_file = pd.concat([pl2_guessor[pl2_guessor.columns[:5]].reset_index(drop=True), pd.Series(pl2_accs, name='Accuracy'), 
                             pd.Series(pl2_rts, name='RT'), pd.DataFrame(pl2_answers)], axis=1).drop(columns=['Role', 'Control?'])
pl2_answer_file.to_csv('/Users/mizwally/Desktop/DYAD_01-tangrams/DYAD_01_SCAN_012_answers.csv', index=False)