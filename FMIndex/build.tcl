# build.tcl
# A reusable script to create different Vivado projects for synthesis or simulation.

# --- Arguments and Variable Definitions ---
set part_name "xcu50-fsvh2104-2-e"
set_param general.maxthreads 4

# The first argument is the target name (e.g., 'synth_1', 'sim_1')
set target [lindex $argv 0]

# The second argument is the mode ('synthesis' or 'simulation')
set mode [lindex $argv 1]

# --- Error Checking ---
if { $target == "" || $mode == "" } {
    puts "ERROR: Usage: vivado -mode batch -source build.tcl -tclargs <target_name> <mode>"
    exit 1
}

# --- Project Creation ---
set proj_name "proj_${target}_${mode}"
set proj_dir "vivado_out/${proj_name}"

puts "INFO: Creating project '${proj_name}'..."
create_project -force ${proj_name} ${proj_dir} -part ${part_name}

# --- Target-specific logic ---
switch $target {
    "sim_1" {
        # --- Add all source files ---
        add_files -fileset sim_1 "src/FM_Index.vhd"
        add_files -fileset sim_1 "src/FM_Index_tb.vhd"

        # Add the simulation top-level testbench
        set_property top FM_Index_tb [get_filesets sim_1]
    }

    default {
        puts "ERROR: Unknown target '$target'."
        exit 1
    }
}

# --- Mode-specific actions ---
switch $mode {
    "synthesis" {
        puts "INFO: Launching synthesis and implementation..."

        # Launch synthesis and implementation
        #launch_runs synth_1
        #wait_on_run synth_1

        #launch_runs impl_1 -to_step write_bitstream
        #wait_on_run impl_1

        start_gui

        puts "INFO: Bitstream for '${target}' complete."
    }
    "simulation" {
        puts "INFO: Launching behavioral simulation..."

        # Create and launch a simulation run
        # create_ip_run -name sim_run_1
        # set_property steps.elaborate.tcl.pre [get_runs sim_run_1] {set_property top sim_top_level_1_tb [get_filesets sim_1]}
        # launch_simulation

        # You can set simulation properties here if needed.
        # For example, to set the simulation run time.
        # set_property xsim.simulate.runtime {15000ns} [current_fileset]

        # Launch the simulation.
        # Use `-gui` to open the waveform viewer after compilation and elaboration.
        # Use `-quiet` or other options if you need a non-interactive run.
        #launch_simulation
        #run 15000ns
        launch_simulation -gui

	# adding a .wcfg file
	open_wave_config src/FM_Index_tb.wcfg	

        start_gui

        puts "INFO: Simulation for '${target}' launched. To view results in GUI, run 'start_gui'."
    }
    default {
        puts "ERROR: Unknown mode '$mode'. Use 'synthesis' or 'simulation'."
        exit 1
    }
}

# --- Final actions ---
# close_project