
selectImage("MTBs_0.5umbeads_20x_10mT_1.20NA_22 Substack (207-410) Substack (176-278).tif");

// Initial Processing
run("RGB Color");
run("8-bit");
run("Watershed", "stack");

// Set measurements to measure (center of ROI)
run("Set Measurements...", "area mean min centroid center stack redirect=None decimal=3");

// Analyze ROIs of particles
run("Analyze Particles...", "clear add stack");

// Delete all info in stacks
run("Select All");
run("Clear", "stack");

// Select all of the ROIs and find their centers
roiManager("Deselect");
roiManager("Measure");

for(var i=1; i < nResults;i++) { 
	// Get position of centroidf
	x = getResult("X", i - 1);
	y = getResult("Y", i - 1);
	toUnscaled(x, y);
	slice = getResult("Slice", i - 1);
	selectImage("MTBs_0.5umbeads_20x_10mT_1.20NA_22 Substack (207-410) Substack (176-278).tif");
	// Set Slice
	setSlice(parseInt(slice));
	// Make an inverted square centered at center
	makeRectangle(x-1, y-1, 3, 3);
	run("Invert", "slice");
}

roiManager("Deselect");
roiManager("Delete");
close("ROI Manager");
close("Results");

