% Script generated by Brainstorm (15-May-2023)

% Input files
sFiles = [];
SubjectNames = {...
    'sub-032407_EC'};
RawFiles = {...
    '/Volumes/ExtremePro/Analyses/LEMON/RAW/EEG_Preprocessed_BIDS_ID/EEG_Preprocessed/sub-032301/sub-032301_EC.set'};

% Start a new report
bst_report('Start', sFiles);

% Process: Import MEG/EEG: Existing epochs
sFiles = bst_process('CallProcess', 'process_import_data_epoch', sFiles, [], ...
    'subjectname',   SubjectNames{1}, ...
    'condition',     '', ...
    'datafile',      {{RawFiles{1}}, 'EEG-EEGLAB'}, ...
    'iepochs',       [], ...
    'eventtypes',    '', ...
    'createcond',    0, ...
    'channelalign',  1, ...
    'usectfcomp',    1, ...
    'usessp',        1, ...
    'freq',          [], ...
    'baseline',      [], ...
    'blsensortypes', 'MEG, EEG');

% Save and display report
ReportFile = bst_report('Save', sFiles);
bst_report('Open', ReportFile);
% bst_report('Export', ReportFile, ExportDir);
% bst_report('Email', ReportFile, username, to, subject, isFullReport);

% Delete temporary files
% gui_brainstorm('EmptyTempFolder');

