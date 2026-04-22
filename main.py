from psychopy import prefs
prefs.hardware['audioLib'] = ['PTB', 'sounddevice', 'pyo', 'pygame'] # type: ignore
from psychopy import visual, core, event, gui, sound
from psychopy.hardware import keyboard
import os, random, csv, time
from pylsl import StreamOutlet, StreamInfo
from sys import platform
from datetime import datetime as dt
import pytz

##Tangrams code for SCANS Project

## if you want to create a stream in this file use this code
info = StreamInfo(name='Trigger1', type='Markers', channel_count=1, channel_format='int32', source_id='Tangrams')  # pyright: ignore[reportArgumentType]
outlet = StreamOutlet(info)
timezone = pytz.timezone('America/New_York')
## Loading screen for participant ID and how to change file order(update the file thing)
info = {'Dyad ID': '', 'Subject ID': '', 'Participant #': '2', 'Run Order': 'A1'}
dlg = gui.DlgFromDict(info, title="Tangrams", order=list(info.keys()))
if not dlg.OK:
    core.quit()

code_interpreter = {"A1": "easy1, hard1, control1, easy2, control2, hard2", 
                    "B1": "hard1, control1, easy1, hard2, easy2, control2",
                    "C1": "control1, hard1, easy1, control2, easy2, hard2",
                    "A2": "easy2, hard2, control2, easy1, control1, hard1",
                    "B2": "hard2, control2, easy2, hard1, easy1, control1",
                    "C2": "control2, hard2, easy2, control1, easy1, hard1"}

folder_code_dict = {'easy1': 1, 'easy2': 2, 'hard1': 3, 'hard2': 4, 'control1': 5, 'control2': 6}
control_index = []
custom_folder_order = []
if len(info['Run Order']) != 2 :
    raise ValueError('Invalid run order; run order a letter and a number')
print(info['Run Order'])
[custom_folder_order.append(k) for k in code_interpreter[info['Run Order']].split(', ')]
print(custom_folder_order)

control_options = [f for f in folder_code_dict.keys() if f not in custom_folder_order]

participant_id = info['Subject ID']
if info['Participant #'] != '1' and info['Participant #'] != '2' :
    raise ValueError('Participant # must be either 1 or 2')

## For Saving file path and data(not sure if this is working yet)
save_path = f"data/{info['Dyad ID']}"
os.makedirs(save_path, exist_ok=True)

csv_file = os.path.join(save_path, f"{info['Dyad ID']}_{participant_id}_abstract-images.csv")
csv_headers = ['Block', 'Round', 'Control?', 'Folder', 'Role', 'Round_start_time', 'Round_end_time',
               'round_duration', 'completion_status',
               'image_1', 'image_2', 'image_3', 'image_4', 'image_5', 'image_6',
               'box_1_input', 'box_1_rt', 'box_2_input', 'box_2_rt', 'box_3_input', 'box_3_rt',
               'box_4_input', 'box_4_rt', 'box_5_input', 'box_5_rt', 'box_6_input', 'box_6_rt',]

with open(csv_file, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(csv_headers)

## Window set up(change window size based on computer used)
win = visual.Window(size=(1500, 850), fullscr=True, color=[0,0,0], units='pix')
mouse = event.Mouse(visible=True, win=win)
kb = keyboard.Keyboard()
kb.clock.reset()

start_text = ("Welcome to the abstract images task!\n\n"
            "For this task you will be working with your partner.\n\n"
            "You will each be assigned the role of either Director or Guessor.\n"
            "These roles will be switched throughout the task.\n\n"
            )

director_text = ("If you are the Director, you will see one image at a time\n"
            "and describe it to the Guessor.\n\n"
            "Each image will appear for 20 seconds.\n\n"
            "Do not use the shapes in the image to describe it.\n"
            )

guessor_text = ("If you are the Guessor, you will see 6 images.\n\n" 
            "The Director will describe an image to you and you have to guess\n"
            "which of the 6 they are describing.\n\n"
            "Type the image number (1-6) into the box below the image.\n\n"
            "You can change your responses anytime during the round.\n\n"
            )

## set up text and sound devices
trigger_test = visual.TextStim(win, text="Trigger test", color='white', height=50)
start = visual.TextStim(win, text=start_text, color='white', height=45, 
                        wrapWidth=1400, pos=(0, 300), anchorVert='top')
guessor_directions = visual.TextStim(win, text=guessor_text, color='white', height=45, 
                                     wrapWidth=1400, pos=(0, 300), anchorVert='top')
director_directions = visual.TextStim(win, text=director_text, color='white', height=45, 
                                      wrapWidth=1400, pos=(0, 300), anchorVert='top')
fixation = visual.TextStim(win, text='+', height=50, color='white')
thanks = visual.TextStim(win, text="Thank you for participating!", color='white')
instruction_text = visual.TextStim(win, text='', height=50, wrapWidth=1400, 
                                   color='white', pos=(0, 150), anchorVert='top')
continue_text = visual.TextStim(win, text="Press space to continue.", color='white', 
                                height=45, wrapWidth=1400, pos=(0, -150), anchorVert='top')
questions_text =  visual.TextStim(win, text="Any questions?", color='white', height=50, 
                                     wrapWidth=1400, pos=(0, 200), anchorVert='top')
start_sound = sound.Sound('D', secs=0.5, stereo=True, hamming=False, name='start_sound')
end_sound = sound.Sound('C', secs=0.5, stereo=True, hamming=False, name='end_sound')

## Image pathway (make sure youy edit directory before running task and that you have the right folders downloaded)
#checking if windows or mac
if platform == "darwin":
    print('Mac OS')
    base_dir = './images'
elif platform == "win32":
    print('Windows')
    base_dir = '.\\images'

all_images = {}
for folder in custom_folder_order:
    full_path = os.path.join(base_dir, folder)
    if os.path.exists(full_path):
        all_images[folder] = [
            os.path.join(full_path, f)
            for f in os.listdir(full_path)
            if f.endswith(('.jpg', '.png'))
        ]
    else:
        all_images[folder] = []

used_images = []

def log_response(block, round, condition, folder, role, start_time, end_time, images, selections, times, rt, status="completed"):
    img_names = [os.path.basename(img) for img in images]
    results = []
    for i in range(len(selections)) :
        results.append(selections[i])
        results.append(times[i])
        print(times[i])
    with open(csv_file, 'a', newline='') as f:
        writer = csv.writer(f)
        #row = [block, condition, folder, role] + img_names + [','.join(map(str, selections)), rt, status]
        row = [block, round, condition, folder, role, start_time, end_time, rt, status] + img_names + results 
        writer.writerow(row)

##Utility functions
def check_escape():
    if 'escape' in event.getKeys():
        log_response('N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', ['']*6, ['']*6, ['']*6, 0.0, status="early_exit")
        win.close()
        core.quit()

def check_escape2(key):
    if key == 'escape':
        log_response('N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', ['']*6, ['']*6, ['']*6, 0.0, status="early_exit")
        win.close()
        core.quit()

def wait_for_space(time):
    space = False
    while not space :  
        check_escape()
        keys = kb.getKeys(keyList=['space'])
        for key in keys :
            if key.rt >= time :
                space = True
                break

def show_fixation(duration=5):
    outlet.push_sample(x=[77])
    fixation.draw()
    win.flip()
    core.wait(duration)
    check_escape()

def select_images(folder, num=6):
    full_path = os.path.join(base_dir, folder)
    if os.path.exists(full_path):
        images = [
            os.path.join(full_path, f)
            for f in os.listdir(full_path)
            if f.endswith(('.jpg', '.png'))
        ]
    else:
        images = []
    #available = list(set(all_images[folder]) - set(used_images))
    #if len(available) < num:
    #    raise ValueError(f"Not enough unique images remaining in folder {folder}")
    selected = random.sample(images, num)
    used_images.extend(selected)
    return selected

def show_instructions(role):
    outlet.push_sample(x=[66])
    check_escape()
    if role == 'guessor':
        instruction = (
            "You are the GUESSOR.\n\n"
        )
    else:
        instruction = (
            "You are the DIRECTOR.\n\n"
        )
    instruction_text.text = instruction
    instruction_text.draw()
    win.flip()
    start = time.time()
    while time.time() - start < 10:
            check_escape()
            core.wait(0.1)

def guessor_block(block_num, round_num, ctrl, folder, images):
    start_time = dt.now(timezone).time().strftime("%H:%M:%S")
    positions = [(-400, 250), (0, 250), (400, 250), (-400, -120), (0, -120), (400, -120)]
    image_stims = [visual.ImageStim(win, image=img, pos=pos, size=(250, 250))
                   for img, pos in zip(images, positions)]

    box_positions = [(-400, 70), (0, 70), (400, 70), (-400, -300), (0, -300), (400, -300)]
    input_boxes = [visual.TextBox2(win, text='', pos=pos, letterHeight=24, editable=True,
                            size=(110, 35), placeholder='', color='black', fillColor='white',
                            borderColor='black') for pos in box_positions]

    time0 = time.time()
    max_duration = 120

    active_box_index = None
    last_text = [''] * 6
    current_text = [''] * 6
    responses = [[] for _ in range(6)]
    times = [[] for _ in range(6)]
    
    while time.time() - time0 < max_duration:
        check_escape()

        for stim in image_stims:
            stim.draw()
        for box in input_boxes:
            #only allow numbers 1-6        
            allowed = ['1', '2', '3', '4', '5', '6', 'backspace'] 
            box.text = "".join(ch for ch in box.text if ch.lower() in allowed)
            if len(box.text) > 1:
                box.text = box.text[0]
            box.draw()

        win.flip()
        
        #for saving values every time they change 
        for i, box in enumerate(input_boxes) :
            if len(box.text) > 1:
                current_text[i] = box.text[0]
            else :
                current_text[i] = box.text
            if current_text[i] != "" and current_text[i] != last_text[i] :
                last_text[i] = current_text[i]  # update tracker
                responses[i].append(current_text[i])
                temp = dt.now(timezone).time().strftime("%H:%M:%S")
                times[i].append(temp)
        
        keys = event.getKeys()
        for key in keys:
            check_escape2(key)
            if key == 'return' and ((time.time() - time0) < 105) :
                #responses = [box.text for box in input_boxes]
                rt = round(time.time() - time0, 3)
                end_time = dt.now(timezone).time().strftime("%H:%M:%S")
                log_response(block_num, round_num, ctrl, folder, 'guessor', start_time, end_time, images, responses, times, rt)
                return
            elif active_box_index is not None:
                if key == 'backspace':
                    input_boxes[active_box_index].text = input_boxes[active_box_index].text[:-1]
                elif len(key) == 1:
                    input_boxes[active_box_index].text += key
    end_time = dt.now(timezone).time().strftime("%H:%M:%S")
    log_response(block_num, round_num, ctrl, folder, 'guessor', start_time, end_time, images, responses, times, round(time.time() - time0, 3))
        
def director_block(block_num, round_num, ctrl, folder, images):
    start_time = dt.now(timezone).time().strftime("%H:%M:%S")
    time0 = time.time()
    for i, img_path in enumerate(images, start=1):
        stim = visual.ImageStim(win, image=img_path, size=(550, 550))
        counter = visual.TextStim(win, text=str(i), pos=(600, -300), color='white', height=30)
        stim.draw()
        counter.draw()
        win.flip()
        time1 = time.time()
        while time.time() - time1 < 20:
            check_escape()
            core.wait(0.1)

    responses = [] * 6
    times = [] * 6
    end_time = dt.now(timezone).time().strftime("%H:%M:%S")
    log_response(block_num, round_num, ctrl, folder, 'director', start_time, end_time, images, responses, times, round(time.time() - time0, 3))
    
block_count = 6
block_num = 0
task_blocks = 0

trigger_test.draw()
win.flip()
wait_for_space(0)
outlet.push_sample(x=[1])
print("trigger test")

clock = core.Clock()
kb.clock.reset()
start_sound.play()
outlet.push_sample(x=[99])
print(99)
while True:
    check_escape()
    t = clock.getTime()
    start.draw()
    if t > 3:
        continue_text.draw()
        win.flip()
        wait_for_space(3)
        break
    win.flip()
    
clock.reset(0)
kb.clock.reset()
while True:
    check_escape()
    t = clock.getTime()
    director_directions.draw()
    if t > 3:
        continue_text.draw()
        win.flip()
        wait_for_space(3)
        break
    win.flip()

#draw director example page
clock.reset(0)
kb.clock.reset()
stim = visual.ImageStim(win, image=f'{base_dir}/intro_images/70.png', size=(550, 550))
counter = visual.TextStim(win, text=str(1), pos=(600, -300), color='white', height=30)
while True:
    check_escape()
    t = clock.getTime()
    stim.draw()
    counter.draw()
    if t > 3:
        wait_for_space(3)
        break
    win.flip()

clock.reset(0)
kb.clock.reset()
while True:
    check_escape()
    t = clock.getTime()
    guessor_directions.draw()
    if t > 3:
        continue_text.draw()
        win.flip()
        wait_for_space(3)
        break
    win.flip()

#draw guessor example page
image_dirs = ['70.png', '71.png', '72.png', '73.png', '74.png', '75.png']
images = [f'{base_dir}/intro_images/{x}' for x in image_dirs]
positions = [(-400, 250), (0, 250), (400, 250), (-400, -120), (0, -120), (400, -120)]
image_stims = [visual.ImageStim(win, image=img, pos=pos, size=(250, 250))
                   for img, pos in zip(images, positions)]
box_positions = [(-400, 70), (0, 70), (400, 70), (-400, -300), (0, -300), (400, -300)]
input_boxes = [visual.TextBox2(win, text='', pos=pos, letterHeight=24, editable=True,
                            size=(110, 35), placeholder='', color='black', fillColor='white',
                            borderColor='black') for pos in box_positions]
clock.reset(0)
kb.clock.reset()
while True:
    check_escape()
    t = clock.getTime()
    for box, stim in zip(input_boxes, image_stims) :
        stim.draw()
        box.draw()
    if t > 3:
        wait_for_space(3)
        break
    win.flip()

clock.reset(0)
kb.clock.reset()
while True:
    check_escape()
    t = clock.getTime()
    questions_text.draw()
    if t > 3:
        continue_text.text = "Please wait for the experimentor to start the task."
        continue_text.draw()
        win.flip()
        wait_for_space(3)
        break
    win.flip()

#looping through blocks
while block_num < block_count :
    folder_index = block_num
    check_escape()
    folder = custom_folder_order[folder_index]
    #task vs control code (trigger 1)
    
    ctrl = False
    if folder == 'control1' or folder == 'control2' :
        ctrl = True
        condition = 1
        if info['Participant #'] == '2' :
            print('original: ', folder)
            if folder == 'control1' :
                folder = 'control2'
            elif folder == 'control2' :
                folder = 'control1'
            print('new: ', folder)
    else :
        condition = 2
        task_blocks += 1
    
    if ctrl == True :
        if info['Participant #'] == '1' :
            role = 'director' if block_num % 2 == 0 else 'guessor'
        else :
            role = 'guessor' if block_num % 2 == 0 else 'director'
    else :
        if task_blocks in [1, 4] :
           role = 'director' if info['Participant #'] == '1' else 'guessor'
        elif task_blocks in [2, 3] :
           role = 'guessor' if info['Participant #'] == '1' else 'director'
    
    for i in range(2) :
        images = select_images(folder, 6)
        #Assigning trigger codes
        #which folder is being used (trigger 2)
        folder_code = folder_code_dict[folder]
        #role code (trigger 3)
        role_code = 1 if role == 'director' else 2
        #first vs repeat block (trigger 4)
        repeat = 1 if i == 0 else 2
        
        #Generating triggers
        cond_trig = condition + 10
        fold_trig = folder_code + 20
        role_trig = role_code + 30
        rep_trig = repeat + 40
        
        show_instructions(role)
        
        outlet.push_sample(x=[cond_trig])
        core.wait(0.05)
        outlet.push_sample(x=[fold_trig])
        core.wait(0.05)
        outlet.push_sample(x=[role_trig])
        core.wait(0.05)
        outlet.push_sample(x=[rep_trig])
        print(cond_trig, fold_trig, role_trig, rep_trig)
        
        if role == 'guessor':
            guessor_block(block_num + 1, repeat, ctrl, folder, images)
        else:
            director_block(block_num + 1, repeat, ctrl, folder, images)
            
        role = 'director' if role == 'guessor' else 'guessor'
        show_fixation()
    block_num += 1

## For the end of the task
thanks.draw()
outlet.push_sample(x=[99])
print(99)
end_sound.play()
win.flip()
core.wait(5)
win.close()
core.quit()