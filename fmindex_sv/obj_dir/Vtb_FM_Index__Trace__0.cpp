// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Tracing implementation internals
#include "verilated_vcd_c.h"
#include "Vtb_FM_Index__Syms.h"


void Vtb_FM_Index___024root__trace_chg_0_sub_0(Vtb_FM_Index___024root* vlSelf, VerilatedVcd::Buffer* bufp);

void Vtb_FM_Index___024root__trace_chg_0(void* voidSelf, VerilatedVcd::Buffer* bufp) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_FM_Index___024root__trace_chg_0\n"); );
    // Init
    Vtb_FM_Index___024root* const __restrict vlSelf VL_ATTR_UNUSED = static_cast<Vtb_FM_Index___024root*>(voidSelf);
    Vtb_FM_Index__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    if (VL_UNLIKELY(!vlSymsp->__Vm_activity)) return;
    // Body
    Vtb_FM_Index___024root__trace_chg_0_sub_0((&vlSymsp->TOP), bufp);
}

void Vtb_FM_Index___024root__trace_chg_0_sub_0(Vtb_FM_Index___024root* vlSelf, VerilatedVcd::Buffer* bufp) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_FM_Index___024root__trace_chg_0_sub_0\n"); );
    Vtb_FM_Index__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Init
    uint32_t* const oldp VL_ATTR_UNUSED = bufp->oldp(vlSymsp->__Vm_baseCode + 1);
    // Body
    if (VL_UNLIKELY((vlSelfRef.__Vm_traceActivity[0U]))) {
        bufp->chgCData(oldp+0,(vlSelfRef.tb_FM_Index__DOT__dut__DOT__C_arr[0]),4);
        bufp->chgCData(oldp+1,(vlSelfRef.tb_FM_Index__DOT__dut__DOT__C_arr[1]),4);
        bufp->chgCData(oldp+2,(vlSelfRef.tb_FM_Index__DOT__dut__DOT__C_arr[2]),4);
        bufp->chgCData(oldp+3,(vlSelfRef.tb_FM_Index__DOT__dut__DOT__C_arr[3]),4);
        bufp->chgCData(oldp+4,(vlSelfRef.tb_FM_Index__DOT__dut__DOT__C_arr[4]),4);
    }
    if (VL_UNLIKELY((vlSelfRef.__Vm_traceActivity[1U]))) {
        bufp->chgBit(oldp+5,(vlSelfRef.tb_FM_Index__DOT__done));
        bufp->chgBit(oldp+6,(vlSelfRef.tb_FM_Index__DOT__fail));
        bufp->chgCData(oldp+7,(vlSelfRef.tb_FM_Index__DOT__dut__DOT__l),4);
        bufp->chgCData(oldp+8,(vlSelfRef.tb_FM_Index__DOT__dut__DOT__r),4);
        bufp->chgCData(oldp+9,(vlSelfRef.tb_FM_Index__DOT__dut__DOT__state),4);
        bufp->chgCData(oldp+10,(vlSelfRef.tb_FM_Index__DOT__dut__DOT__rank_l),4);
        bufp->chgCData(oldp+11,(vlSelfRef.tb_FM_Index__DOT__dut__DOT__rank_r),4);
        bufp->chgCData(oldp+12,(vlSelfRef.tb_FM_Index__DOT__dut__DOT__c),3);
        bufp->chgIData(oldp+13,(vlSelfRef.tb_FM_Index__DOT__dut__DOT__pat_idx),32);
        bufp->chgIData(oldp+14,(vlSelfRef.tb_FM_Index__DOT__dut__DOT__loop_count),32);
    }
    bufp->chgBit(oldp+15,(vlSelfRef.tb_FM_Index__DOT__clk));
    bufp->chgBit(oldp+16,(vlSelfRef.tb_FM_Index__DOT__reset));
    bufp->chgBit(oldp+17,(vlSelfRef.tb_FM_Index__DOT__start));
    bufp->chgIData(oldp+18,(vlSelfRef.tb_FM_Index__DOT__pattern),24);
    bufp->chgIData(oldp+19,(vlSelfRef.tb_FM_Index__DOT__pat_len_in),32);
}

void Vtb_FM_Index___024root__trace_cleanup(void* voidSelf, VerilatedVcd* /*unused*/) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_FM_Index___024root__trace_cleanup\n"); );
    // Init
    Vtb_FM_Index___024root* const __restrict vlSelf VL_ATTR_UNUSED = static_cast<Vtb_FM_Index___024root*>(voidSelf);
    Vtb_FM_Index__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    // Body
    vlSymsp->__Vm_activity = false;
    vlSymsp->TOP.__Vm_traceActivity[0U] = 0U;
    vlSymsp->TOP.__Vm_traceActivity[1U] = 0U;
}
