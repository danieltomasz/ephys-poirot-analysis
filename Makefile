add-assr:
	cd studies/meg-assr & git add . 

clean:
	conda clean -all
	brew cleanup
	pip cache purge