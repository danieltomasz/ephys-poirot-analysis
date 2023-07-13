clear
cd('/mnt/raid/RU1/software/brainstorm3/')
brainstorm %server

addpath(genpath('/mnt/raid/RU1/Analysis_scripts_code/LEMON_analyses/functions/'));

ProtocolName = 'LEMON_ver1';
iProtocol = bst_get('Protocol', ProtocolName);
gui_brainstorm('SetCurrentProtocol', iProtocol);


my_subjects = bst_get('ProtocolSubjects');
Subj_names = {my_subjects.Subject.Name};
Subj_names = setdiff(Subj_names, {'Group_analysis', 'Digitize'}); % exclude Group_analysis

condition_names = {'_EC', '_EO'};


%% create custom report
export_name = '/mnt/raid/RU1/Analysis_scripts_code/LEMON_analyses/Step2_1_report.txt';
fid = fopen(export_name, 'w')

% for iSubj = 199:202(Subj_names)

for iSubj = 1:3 %iSubj = 1:length(Subj_names)
    
    curr_subj = Subj_names{iSubj};
    
    for iCond = 1:length(condition_names)
        
        curr_cond = condition_names{iCond};
        
        % select subject files with bst function
        temp_files = bst_process('CallProcess', 'process_select_files_results', [], [], ...
            'subjectname',   curr_subj, ...
            'condition',     '', ...
            'tag',           '', ...
            'includebad',    0, ...
            'includeintra',  0, ...
            'includecommon', 0);
        
        temp_filenames = {temp_files.FileName};
        
        trial_filenames = sel_files_bst(temp_filenames, curr_cond);
        trial_filenames = sel_files_bst(trial_filenames, 'block');
        
        
        trial_filenames_std = sel_files_bst(trial_filenames, 'std_chan');
        
        % if there are any std files use only those
        if length(trial_filenames_std)>0
            trial_filenames = trial_filenames_std; 
        end;
        
        % Start a new report
        bst_report('Start', trial_filenames);
        
        
        % Process: Power spectrum density (Welch)
        PSD_files = bst_process('CallProcess', 'process_psd', trial_filenames, [], ...
            'timewindow',  [], ...
            'win_length',  1, ...
            'win_overlap', 50, ...
            'clusters',    {'Desikan-Killiany', {'bankssts L', 'bankssts R', 'caudalanteriorcingulate L', 'caudalanteriorcingulate R', 'caudalmiddlefrontal L', 'caudalmiddlefrontal R', 'cuneus L', 'cuneus R', 'entorhinal L', 'entorhinal R', 'frontalpole L', 'frontalpole R', 'fusiform L', 'fusiform R', 'inferiorparietal L', 'inferiorparietal R', 'inferiortemporal L', 'inferiortemporal R', 'insula L', 'insula R', 'isthmuscingulate L', 'isthmuscingulate R', 'lateraloccipital L', 'lateraloccipital R', 'lateralorbitofrontal L', 'lateralorbitofrontal R', 'lingual L', 'lingual R', 'medialorbitofrontal L', 'medialorbitofrontal R', 'middletemporal L', 'middletemporal R', 'paracentral L', 'paracentral R', 'parahippocampal L', 'parahippocampal R', 'parsopercularis L', 'parsopercularis R', 'parsorbitalis L', 'parsorbitalis R', 'parstriangularis L', 'parstriangularis R', 'pericalcarine L', 'pericalcarine R', 'postcentral L', 'postcentral R', 'posteriorcingulate L', 'posteriorcingulate R', 'precentral L', 'precentral R', 'precuneus L', 'precuneus R', 'rostralanteriorcingulate L', 'rostralanteriorcingulate R', 'rostralmiddlefrontal L', 'rostralmiddlefrontal R', 'superiorfrontal L', 'superiorfrontal R', 'superiorparietal L', 'superiorparietal R', 'superiortemporal L', 'superiortemporal R', 'supramarginal L', 'supramarginal R', 'temporalpole L', 'temporalpole R', 'transversetemporal L', 'transversetemporal R'}}, ...
            'scoutfunc',   3, ...  % PCA
            'win_std',     0, ...
            'edit',        struct(...
            'Comment',         'Scouts,Avg,Power', ...
            'TimeBands',       [], ...
            'Freqs',           [], ...
            'ClusterFuncTime', 'before', ...
            'Measure',         'power', ...
            'Output',          'average', ...
            'SaveKernel',      0));
        
        % Process: Add tag: post-ica
        PSD_files = bst_process('CallProcess', 'process_add_tag',PSD_files, [], ...
            'tag',           curr_cond, ...
            'output',        1);  % Add to file name
        
        % Process: Add tag: post-ica
        PSD_files = bst_process('CallProcess', 'process_add_tag', PSD_files, [], ...
            'tag',           curr_cond, ...
            'output',        2);  % Add to file name
              
        
        ReportFile = bst_report('Save', []);
        bst_report('Open', ReportFile);
        
    end;
    
end;

fclose(fid); % close report
