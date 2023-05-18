% Export atlas time-series as mat file
% Add brainstorm to path
%pathStr = '/Users/GPellegrino/Documents/brainstorm3';
%addpath(genpath(pathStr));
%run brainstorm. The first time you need to open the graphical interface
if ~brainstorm('status')
    brainstorm server
end
% Select folder for output
Output_folder = '/Volumes/ExtremePro/Analyses/tDCS_MEG/brainstorm/'
%% Select protocol name
ProtocolName = 'tDCS_MEG_Marinazzo';
% get the protocol index, knowing the name
iProtocol = bst_get('Protocol', ProtocolName);
% set the current protocol
gui_brainstorm('SetCurrentProtocol', iProtocol);
ProtocolInfo=bst_get('ProtocolInfo'); 
my_subjects = bst_get('ProtocolSubjects');
% loop over subjects
for jh=1:length(my_subjects.Subject)
    iSubject=bst_get('Subject',jh);
    if isempty(strfind(iSubject.Name, 'Group_analysis'))
        Subject_Studies=bst_get('StudyWithSubject', iSubject.FileName);
        % loop over subject's folders
        for sd=1:length(Subject_Studies)
            if isempty(strfind(string(Subject_Studies(sd).Condition), 'CAT12'))
                % find the 'study'
                [sStudy, iStudy]= bst_get('Study', Subject_Studies(sd).FileName);
                % find all source files of the folder
                sFiles = bst_process('CallProcess', 'process_select_files_results', [], [], ...
                    'subjectname',   iSubject.Name, ...
                    'condition',     sStudy.Name, ...
                    'tag',           [], ...
                    'includebad',    0, ...
                    'includeintra',  0, ... % include intra as I select average of runs
                    'includecommon', 0);
                % Process: Scouts time series
                sFiles = bst_process('CallProcess', 'process_extract_scout', sFiles, [], ...
                    'timewindow',     [], ...
                    'scouts',         {'Desikan-Killiany', {'bankssts L', 'bankssts R', 'caudalanteriorcingulate L', 'caudalanteriorcingulate R', 'caudalmiddlefrontal L', 'caudalmiddlefrontal R', 'cuneus L', 'cuneus R', 'entorhinal L', 'entorhinal R', 'frontalpole L', 'frontalpole R', 'fusiform L', 'fusiform R', 'inferiorparietal L', 'inferiorparietal R', 'inferiortemporal L', 'inferiortemporal R', 'insula L', 'insula R', 'isthmuscingulate L', 'isthmuscingulate R', 'lateraloccipital L', 'lateraloccipital R', 'lateralorbitofrontal L', 'lateralorbitofrontal R', 'lingual L', 'lingual R', 'medialorbitofrontal L', 'medialorbitofrontal R', 'middletemporal L', 'middletemporal R', 'paracentral L', 'paracentral R', 'parahippocampal L', 'parahippocampal R', 'parsopercularis L', 'parsopercularis R', 'parsorbitalis L', 'parsorbitalis R', 'parstriangularis L', 'parstriangularis R', 'pericalcarine L', 'pericalcarine R', 'postcentral L', 'postcentral R', 'posteriorcingulate L', 'posteriorcingulate R', 'precentral L', 'precentral R', 'precuneus L', 'precuneus R', 'rostralanteriorcingulate L', 'rostralanteriorcingulate R', 'rostralmiddlefrontal L', 'rostralmiddlefrontal R', 'superiorfrontal L', 'superiorfrontal R', 'superiorparietal L', 'superiorparietal R', 'superiortemporal L', 'superiortemporal R', 'supramarginal L', 'supramarginal R', 'temporalpole L', 'temporalpole R', 'transversetemporal L', 'transversetemporal R'}}, ...
                    'scoutfunc',      1, ...  % Takes the mean of the parce time series
                    'isflip',         0, ...  % If 1, flips the sign of the signals so to avoid cancellation
                    'isnorm',         0, ...
                    'concatenate',    0, ...
                    'save',           1, ...
                    'addrowcomment',  1, ...
                    'addfilecomment', 1);
                % now time-series have been generated and saved into brainstorm format. We
                % will loop over these files and save them outside brainstorm
                for as = 1: length (sFiles)
                    temp_tile = load (file_fullpath(sFiles(as).FileName));
                    Output_FileName = ([Output_folder iSubject.Name '_' char(Subject_Studies(sd).Condition) '_' num2str(as)]);
                    save(Output_FileName, '-struct', 'temp_tile');
                end
                % Now let's delete these files from brainstorm database, so that they do
                % not take space (unless you wanna keep them)
                sFiles = bst_process('CallProcess', 'process_delete', sFiles, [], ...
                    'target', 1);  % Delete selected files
            end
        end
    end
end