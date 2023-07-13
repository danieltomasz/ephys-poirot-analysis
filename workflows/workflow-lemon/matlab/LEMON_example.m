

%%%%%
cd('/Volumes/ExtremePro/Analyses/LEMON/RAW/EEG_Preprocessed_BIDS_ID/EEG_Preprocessed')

files_EO=dir('sub*/sub*.set');

sFiles = [];
nsubj= 50; 

firstSubject = 191;
lastSubject = 203;
%%% 

% make subject names
for i = firstSubject:lastSubject
    db_reload_database('current');
    subjectname{i} = files_EO(i,1).name(1:13);
    [sSubject{i}, iSubject] = db_add_subject(subjectname{i});

end
      

for i = firstSubject:lastSubject
    % Process: Create link to set file
   
    sFiles = bst_process('CallProcess', 'process_import_data_epoch', sFiles, [], ...
        'subjectname',  subjectname{i}, ...
        'condition',     '', ...
        'datafile',      {{strcat(files_EO(i,1).folder, '/', files_EO(i,1).name)}, 'EEG-EEGLAB'}, ...
        'iepochs',       [], ...
        'eventtypes',    '', ...
        'createcond',    0, ...
        'channelalign',  1, ...
        'usectfcomp',    1, ...
        'usessp',        1, ...
        'freq',          [], ...
        'baseline',      [], ...
        'blsensortypes', 'MEG, EEG');

end

% Define subjec