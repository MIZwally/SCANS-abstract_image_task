<strong>Abstract Images Task</strong>

This task involves 2 participants and 2 roles (director and guessor). Each participant is assigned a number, either 1 or 2, which determines their initial role. This script can be run for both participants at the same time with the input of their number.

The goal of the task is for the guessor to correctly guess which image the director is describing. The guessor sees 6 different images and the director sees 1 at a time, rotating through and describing each of the 6 images that the guessor sees. After one round, the roles switch; the director becomes the new guessor while the guessor becomes the new director. The images do not change with the role switch, so the new director is now describing the images that they were guessing between, and the new guessor is guessing from the images that they just described.

Each iteration of this pattern is considered a block, with the set of images changing for each block. There are 2 types of blocks: task blocks and control blocks. Task blocks are as explained above, and can be either easy or hard. Easy images are generally easier to describe than harder images. For the control blocks, the director and guessor do not see the same set of images, so the director will be explaining different images than the set that the guessor can choose from.

Our paradigm contains 6 blocks; 2 easy, 2 hard, and 2 control blocks spread throughout the task. The order of these blocks is preassigned and counterbalanced via a "run order code." 

<strong>Run Order Code Interpretation:</strong>

A1:	easy1, hard1, control1, easy2, control2, hard2 &emsp;&emsp;&emsp;&emsp; 
A2:	easy2, hard2, control2, easy1, control1, hard1\
B1:	hard1, control1, easy1, hard2, easy2, control2 &emsp;&emsp;&emsp;&emsp;
B2:	hard2, control2, easy2, hard1, easy1, control1\
C1:	control1, hard1, easy1, control2, easy2, hard2 &emsp;&emsp;&emsp;&emsp;
C2:	control2, hard2, easy2, control1, easy1, hard1

Note that the control images should not be the same for the participants, so participant 2 will see the opposite control folder to participant 1 (this is written into the program).

This task is designed to be used with fNIRS technology, so Lab Streaming Layer (LSL) triggers are embedded into the code to mark the data at different events. Each block will have 6 triggers, with each trigger type occuring twice. First there will be a fixation trigger for the fixation period, followed by an instructions triggern for the instructions window, then a run trigger for the round of the images task. The run triggers change depending on the block type (task or control), the set of images (easy vs hard vs control, 1 vs 2), whether the participant role is director or guessor, and whether or not this is the first round or a second round in a block. Each of these variables is part of a series of back-to-back triggers, with the first digit indicating which trigger it is, and the second digit being the actual value to encode.

Condition - value + 10 (11 for control, 12 for task)
Folder - value + 20 (ex: 23)
Role - value + 30 (31 for director, 32 for guessor)
Repeat - value + 40 (41 for first iteration, 42 for second)

There are are other triggers, such as the fixation and instructions triggers, that are static in value. See below for those triggers and their values.

<strong> Static Triggers:</strong>

0 - start of experiment\
66 - fixation\
77 - instructions\
99 - end of experiment

<strong> Dependencies </strong>

See the uv.lock and pyproject.toml files for dependencies. The package pylsl requires liblsl, which must be downloaded independently on Mac OS computers. See the package documentation for more details.