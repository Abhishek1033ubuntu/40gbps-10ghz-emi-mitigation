"""
Ansys HFSS Automation Script via PyAEDT (50 GHz Compliant Setup)
Constructs 4-Channel 50-Ohm GSG Stripline with Tightened SIW Via Fences (p = 0.50 mm)

Author: Abhishek Singh (ORCID: 0009-0004-6913-096X)
License: MIT
"""

import sys
from pyaedt import Hfss

def run_hfss_simulation_50g():
    desktop_version = "2024.1"
    non_graphical = False

    hfss = Hfss(
        projectname="GSG_4Channel_50GHz_SIW",
        designname="MultiChannel_GSG_Stripline_50GHz",
        specified_version=desktop_version,
        non_graphical=non_graphical,
        new_desktop_session=True
    )

    hfss.modeler.model_units = "mm"

    # Dimensions (mm)
    L_sub = 10.0
    W_sub = 2.0
    B_dielectric = 0.220
    h_layer = 0.09685

    w_trace = 0.075
    t_cu = 0.020
    t_nife = 0.005
    t_agpd = 0.0013
    t_total_trace = t_cu + t_nife + t_agpd

    # Tightened SIW via pitch for 50 GHz surface wave suppression
    d_via = 0.200
    pitch_via = 0.500   # Updated from 0.800 mm to 0.500 mm (p <= lambda_g / 6)
    s_via_clearance = 0.225

    num_channels = 4
    z_ground_planes = [i * B_dielectric for i in range(num_channels + 1)]

    # Materials
    mat_ro4350b = hfss.materials.add_material("Rogers_RO4350B_Custom")
    mat_ro4350b.permittivity = 3.66
    mat_ro4350b.dielectric_loss_tangent = 0.0037

    mat_agpd = hfss.materials.add_material("Ag_2p5Pd_Alloy")
    mat_agpd.conductivity = 5.82e7

    mat_nife = hfss.materials.add_material("Permalloy_NiFe")
    mat_nife.conductivity = 4.5e6
    mat_nife.permeability = 100.0

    # Substrate Box
    hfss.modeler.create_box(
        position=[-W_sub / 2.0, 0.0, 0.0],
        dimensions=[W_sub, L_sub, num_channels * B_dielectric],
        name="Substrate_RO4350B",
        matname="Rogers_RO4350B_Custom"
    )

    # Ground Planes
    for i, z_gnd in enumerate(z_ground_planes):
        hfss.modeler.create_box(
            position=[-W_sub / 2.0, 0.0, z_gnd - 0.005],
            dimensions=[W_sub, L_sub, 0.010],
            name=f"Ground_Plane_L{i+1}",
            matname="copper"
        )

    # 3-Tier FGM Traces
    for ch in range(num_channels):
        z_center = (ch * B_dielectric) + h_layer + (t_total_trace / 2.0)
        
        hfss.modeler.create_box(
            position=[-w_trace / 2.0, 0.0, z_center - t_total_trace/2.0],
            dimensions=[w_trace, L_sub, t_cu],
            name=f"Ch{ch+1}_Cu_Core",
            matname="copper"
        )
        hfss.modeler.create_box(
            position=[-w_trace / 2.0, 0.0, z_center - t_total_trace/2.0 + t_cu],
            dimensions=[w_trace, L_sub, t_nife],
            name=f"Ch{ch+1}_NiFe_Absorber",
            matname="Permalloy_NiFe"
        )
        hfss.modeler.create_box(
            position=[-w_trace / 2.0, 0.0, z_center - t_total_trace/2.0 + t_cu + t_nife],
            dimensions=[w_trace, L_sub, t_agpd],
            name=f"Ch{ch+1}_AgPd_Cladding",
            matname="Ag_2p5Pd_Alloy"
        )

    # Tightened SIW Via Fences (p = 0.50 mm)
    via_positions_x = [-s_via_clearance, s_via_clearance]
    num_vias_y = int(L_sub / pitch_via)

    for side_x in via_positions_x:
        for v_idx in range(num_vias_y + 1):
            y_pos = v_idx * pitch_via
            if y_pos <= L_sub:
                hfss.modeler.create_cylinder(
                    orientation="Z",
                    origin=[side_x, y_pos, 0.0],
                    radius=d_via / 2.0,
                    height=num_channels * B_dielectric,
                    name=f"SIW_Via_X{side_x:.2f}_Y{y_pos:.2f}",
                    matname="copper"
                )

    # Wave Ports
    for ch in range(num_channels):
        z_min = ch * B_dielectric
        
        port_in = hfss.modeler.create_rectangle(
            orientation="Y",
            origin=[-W_sub / 2.0, 0.0, z_min],
            sizes=[W_sub, B_dielectric],
            name=f"Port_Sheet_Ch{ch+1}_In"
        )
        hfss.wave_port_multimodal(assignment=port_in.name, modes=1, port_name=f"P{ch+1}_In")

        port_out = hfss.modeler.create_rectangle(
            orientation="Y",
            origin=[-W_sub / 2.0, L_sub, z_min],
            sizes=[W_sub, B_dielectric],
            name=f"Port_Sheet_Ch{ch+1}_Out"
        )
        hfss.wave_port_multimodal(assignment=port_out.name, modes=1, port_name=f"P{ch+1}_Out")

    # Setup 50 GHz Adaptive Frequency Sweep
    setup = hfss.create_setup(name="Setup_50GHz")
    setup.props["Frequency"] = "50.0GHz"
    setup.props["MaxDeltaS"] = 0.01
    setup.props["MaximumPasses"] = 18

    hfss.create_frequency_sweep(
        setup="Setup_50GHz",
        sweep_type="Interpolating",
        sweep_name="Sweep_100kHz_50GHz",
        start_frequency="100kHz",
        stop_frequency="50.0GHz",
        num_of_freq_points=501
    )

    hfss.save_project()
    print("=== 50 GHz HFSS MODEL CONSTRUCTED & SAVED SUCCESSFULLY ===")

if __name__ == "__main__":
    run_hfss_simulation_50g()
