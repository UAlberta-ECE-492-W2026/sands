// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See Vtb_FM_Index.h for the primary calling header

#include "Vtb_FM_Index__pch.h"
#include "Vtb_FM_Index___024root.h"

VL_ATTR_COLD void Vtb_FM_Index___024root___eval_static__TOP(Vtb_FM_Index___024root* vlSelf);
VL_ATTR_COLD void Vtb_FM_Index___024root____Vm_traceActivitySetAll(Vtb_FM_Index___024root* vlSelf);

VL_ATTR_COLD void Vtb_FM_Index___024root___eval_static(Vtb_FM_Index___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_FM_Index___024root___eval_static\n"); );
    Vtb_FM_Index__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    Vtb_FM_Index___024root___eval_static__TOP(vlSelf);
    Vtb_FM_Index___024root____Vm_traceActivitySetAll(vlSelf);
    vlSelfRef.__Vtrigprevexpr___TOP__tb_FM_Index__DOT__clk__0 
        = vlSelfRef.tb_FM_Index__DOT__clk;
}

VL_ATTR_COLD void Vtb_FM_Index___024root___eval_static__TOP(Vtb_FM_Index___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_FM_Index___024root___eval_static__TOP\n"); );
    Vtb_FM_Index__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.tb_FM_Index__DOT__dut__DOT__C_arr[0U] = 0U;
    vlSelfRef.tb_FM_Index__DOT__dut__DOT__C_arr[1U] = 1U;
    vlSelfRef.tb_FM_Index__DOT__dut__DOT__C_arr[2U] = 4U;
    vlSelfRef.tb_FM_Index__DOT__dut__DOT__C_arr[3U] = 5U;
    vlSelfRef.tb_FM_Index__DOT__dut__DOT__C_arr[4U] = 6U;
    vlSelfRef.tb_FM_Index__DOT__dut__DOT__Occ[0U][0U] = 0U;
    vlSelfRef.tb_FM_Index__DOT__dut__DOT__Occ[0U][1U] = 0U;
    vlSelfRef.tb_FM_Index__DOT__dut__DOT__Occ[0U][2U] = 0U;
    vlSelfRef.tb_FM_Index__DOT__dut__DOT__Occ[0U][3U] = 0U;
    vlSelfRef.tb_FM_Index__DOT__dut__DOT__Occ[0U][4U] = 0U;
    vlSelfRef.tb_FM_Index__DOT__dut__DOT__Occ[0U][5U] = 0U;
    vlSelfRef.tb_FM_Index__DOT__dut__DOT__Occ[0U][6U] = 0U;
    vlSelfRef.tb_FM_Index__DOT__dut__DOT__Occ[0U][7U] = 0U;
    vlSelfRef.tb_FM_Index__DOT__dut__DOT__Occ[0U][8U] = 0U;
    vlSelfRef.tb_FM_Index__DOT__dut__DOT__Occ[1U][0U] = 0U;
    vlSelfRef.tb_FM_Index__DOT__dut__DOT__Occ[1U][1U] = 1U;
    vlSelfRef.tb_FM_Index__DOT__dut__DOT__Occ[1U][2U] = 1U;
    vlSelfRef.tb_FM_Index__DOT__dut__DOT__Occ[1U][3U] = 1U;
    vlSelfRef.tb_FM_Index__DOT__dut__DOT__Occ[1U][4U] = 1U;
    vlSelfRef.tb_FM_Index__DOT__dut__DOT__Occ[1U][5U] = 2U;
    vlSelfRef.tb_FM_Index__DOT__dut__DOT__Occ[1U][6U] = 2U;
    vlSelfRef.tb_FM_Index__DOT__dut__DOT__Occ[1U][7U] = 2U;
    vlSelfRef.tb_FM_Index__DOT__dut__DOT__Occ[1U][8U] = 3U;
    vlSelfRef.tb_FM_Index__DOT__dut__DOT__Occ[2U][0U] = 0U;
    vlSelfRef.tb_FM_Index__DOT__dut__DOT__Occ[2U][1U] = 0U;
    vlSelfRef.tb_FM_Index__DOT__dut__DOT__Occ[2U][2U] = 1U;
    vlSelfRef.tb_FM_Index__DOT__dut__DOT__Occ[2U][3U] = 1U;
    vlSelfRef.tb_FM_Index__DOT__dut__DOT__Occ[2U][4U] = 1U;
    vlSelfRef.tb_FM_Index__DOT__dut__DOT__Occ[2U][5U] = 1U;
    vlSelfRef.tb_FM_Index__DOT__dut__DOT__Occ[2U][6U] = 1U;
    vlSelfRef.tb_FM_Index__DOT__dut__DOT__Occ[2U][7U] = 1U;
    vlSelfRef.tb_FM_Index__DOT__dut__DOT__Occ[2U][8U] = 1U;
    vlSelfRef.tb_FM_Index__DOT__dut__DOT__Occ[3U][0U] = 0U;
    vlSelfRef.tb_FM_Index__DOT__dut__DOT__Occ[3U][1U] = 0U;
    vlSelfRef.tb_FM_Index__DOT__dut__DOT__Occ[3U][2U] = 0U;
    vlSelfRef.tb_FM_Index__DOT__dut__DOT__Occ[3U][3U] = 0U;
    vlSelfRef.tb_FM_Index__DOT__dut__DOT__Occ[3U][4U] = 1U;
    vlSelfRef.tb_FM_Index__DOT__dut__DOT__Occ[3U][5U] = 1U;
    vlSelfRef.tb_FM_Index__DOT__dut__DOT__Occ[3U][6U] = 1U;
    vlSelfRef.tb_FM_Index__DOT__dut__DOT__Occ[3U][7U] = 1U;
    vlSelfRef.tb_FM_Index__DOT__dut__DOT__Occ[3U][8U] = 1U;
    vlSelfRef.tb_FM_Index__DOT__dut__DOT__Occ[4U][0U] = 0U;
    vlSelfRef.tb_FM_Index__DOT__dut__DOT__Occ[4U][1U] = 0U;
    vlSelfRef.tb_FM_Index__DOT__dut__DOT__Occ[4U][2U] = 0U;
    vlSelfRef.tb_FM_Index__DOT__dut__DOT__Occ[4U][3U] = 1U;
    vlSelfRef.tb_FM_Index__DOT__dut__DOT__Occ[4U][4U] = 1U;
    vlSelfRef.tb_FM_Index__DOT__dut__DOT__Occ[4U][5U] = 1U;
    vlSelfRef.tb_FM_Index__DOT__dut__DOT__Occ[4U][6U] = 1U;
    vlSelfRef.tb_FM_Index__DOT__dut__DOT__Occ[4U][7U] = 2U;
    vlSelfRef.tb_FM_Index__DOT__dut__DOT__Occ[4U][8U] = 2U;
}

VL_ATTR_COLD void Vtb_FM_Index___024root___eval_final(Vtb_FM_Index___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_FM_Index___024root___eval_final\n"); );
    Vtb_FM_Index__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
}

VL_ATTR_COLD void Vtb_FM_Index___024root___eval_settle(Vtb_FM_Index___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_FM_Index___024root___eval_settle\n"); );
    Vtb_FM_Index__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
}

#ifdef VL_DEBUG
VL_ATTR_COLD void Vtb_FM_Index___024root___dump_triggers__act(Vtb_FM_Index___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_FM_Index___024root___dump_triggers__act\n"); );
    Vtb_FM_Index__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if ((1U & (~ vlSelfRef.__VactTriggered.any()))) {
        VL_DBG_MSGF("         No triggers active\n");
    }
    if ((1ULL & vlSelfRef.__VactTriggered.word(0U))) {
        VL_DBG_MSGF("         'act' region trigger index 0 is active: @(posedge tb_FM_Index.clk)\n");
    }
    if ((2ULL & vlSelfRef.__VactTriggered.word(0U))) {
        VL_DBG_MSGF("         'act' region trigger index 1 is active: @([true] __VdlySched.awaitingCurrentTime())\n");
    }
}
#endif  // VL_DEBUG

#ifdef VL_DEBUG
VL_ATTR_COLD void Vtb_FM_Index___024root___dump_triggers__nba(Vtb_FM_Index___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_FM_Index___024root___dump_triggers__nba\n"); );
    Vtb_FM_Index__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if ((1U & (~ vlSelfRef.__VnbaTriggered.any()))) {
        VL_DBG_MSGF("         No triggers active\n");
    }
    if ((1ULL & vlSelfRef.__VnbaTriggered.word(0U))) {
        VL_DBG_MSGF("         'nba' region trigger index 0 is active: @(posedge tb_FM_Index.clk)\n");
    }
    if ((2ULL & vlSelfRef.__VnbaTriggered.word(0U))) {
        VL_DBG_MSGF("         'nba' region trigger index 1 is active: @([true] __VdlySched.awaitingCurrentTime())\n");
    }
}
#endif  // VL_DEBUG

VL_ATTR_COLD void Vtb_FM_Index___024root____Vm_traceActivitySetAll(Vtb_FM_Index___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_FM_Index___024root____Vm_traceActivitySetAll\n"); );
    Vtb_FM_Index__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.__Vm_traceActivity[0U] = 1U;
    vlSelfRef.__Vm_traceActivity[1U] = 1U;
}

VL_ATTR_COLD void Vtb_FM_Index___024root___ctor_var_reset(Vtb_FM_Index___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_FM_Index___024root___ctor_var_reset\n"); );
    Vtb_FM_Index__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    const uint64_t __VscopeHash = VL_MURMUR64_HASH(vlSelf->name());
    vlSelf->tb_FM_Index__DOT__clk = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 2885557336182822153ull);
    vlSelf->tb_FM_Index__DOT__reset = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 17621325175104932403ull);
    vlSelf->tb_FM_Index__DOT__start = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 1606714436727396466ull);
    vlSelf->tb_FM_Index__DOT__pattern = VL_SCOPED_RAND_RESET_I(24, __VscopeHash, 17897170817066636906ull);
    vlSelf->tb_FM_Index__DOT__pat_len_in = 0;
    vlSelf->tb_FM_Index__DOT__done = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 3359964158276153336ull);
    vlSelf->tb_FM_Index__DOT__fail = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 11881266088214854743ull);
    vlSelf->tb_FM_Index__DOT__dut__DOT__state = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 16531893655913256140ull);
    vlSelf->tb_FM_Index__DOT__dut__DOT__l = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 1468373601619198392ull);
    vlSelf->tb_FM_Index__DOT__dut__DOT__r = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 7210045631188475433ull);
    vlSelf->tb_FM_Index__DOT__dut__DOT__rank_l = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 18256934118141917485ull);
    vlSelf->tb_FM_Index__DOT__dut__DOT__rank_r = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 17846515935226448567ull);
    vlSelf->tb_FM_Index__DOT__dut__DOT__c = VL_SCOPED_RAND_RESET_I(3, __VscopeHash, 1434609220478026851ull);
    vlSelf->tb_FM_Index__DOT__dut__DOT__pat_idx = 0;
    vlSelf->tb_FM_Index__DOT__dut__DOT__loop_count = 0;
    for (int __Vi0 = 0; __Vi0 < 5; ++__Vi0) {
        vlSelf->tb_FM_Index__DOT__dut__DOT__C_arr[__Vi0] = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 4700927212433814131ull);
    }
    for (int __Vi0 = 0; __Vi0 < 5; ++__Vi0) {
        for (int __Vi1 = 0; __Vi1 < 9; ++__Vi1) {
            vlSelf->tb_FM_Index__DOT__dut__DOT__Occ[__Vi0][__Vi1] = VL_SCOPED_RAND_RESET_I(4, __VscopeHash, 2713283800318858564ull);
        }
    }
    vlSelf->__Vtrigprevexpr___TOP__tb_FM_Index__DOT__clk__0 = VL_SCOPED_RAND_RESET_I(1, __VscopeHash, 8009231319693867185ull);
    for (int __Vi0 = 0; __Vi0 < 2; ++__Vi0) {
        vlSelf->__Vm_traceActivity[__Vi0] = 0;
    }
}
