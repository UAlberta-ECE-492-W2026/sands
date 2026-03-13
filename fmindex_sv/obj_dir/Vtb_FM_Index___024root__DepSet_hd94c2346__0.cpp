// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See Vtb_FM_Index.h for the primary calling header

#include "Vtb_FM_Index__pch.h"
#include "Vtb_FM_Index___024root.h"

VlCoroutine Vtb_FM_Index___024root___eval_initial__TOP__Vtiming__0(Vtb_FM_Index___024root* vlSelf);
VlCoroutine Vtb_FM_Index___024root___eval_initial__TOP__Vtiming__1(Vtb_FM_Index___024root* vlSelf);

void Vtb_FM_Index___024root___eval_initial(Vtb_FM_Index___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_FM_Index___024root___eval_initial\n"); );
    Vtb_FM_Index__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    Vtb_FM_Index___024root___eval_initial__TOP__Vtiming__0(vlSelf);
    Vtb_FM_Index___024root___eval_initial__TOP__Vtiming__1(vlSelf);
}

VL_INLINE_OPT VlCoroutine Vtb_FM_Index___024root___eval_initial__TOP__Vtiming__0(Vtb_FM_Index___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_FM_Index___024root___eval_initial__TOP__Vtiming__0\n"); );
    Vtb_FM_Index__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.tb_FM_Index__DOT__clk = 0U;
    while (1U) {
        co_await vlSelfRef.__VdlySched.delay(5ULL, 
                                             nullptr, 
                                             "tb_FM_Index.sv", 
                                             36);
        vlSelfRef.tb_FM_Index__DOT__clk = (1U & (~ (IData)(vlSelfRef.tb_FM_Index__DOT__clk)));
    }
}

VL_INLINE_OPT VlCoroutine Vtb_FM_Index___024root___eval_initial__TOP__Vtiming__1(Vtb_FM_Index___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_FM_Index___024root___eval_initial__TOP__Vtiming__1\n"); );
    Vtb_FM_Index__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.tb_FM_Index__DOT__reset = 1U;
    vlSelfRef.tb_FM_Index__DOT__start = 0U;
    vlSelfRef.tb_FM_Index__DOT__pat_len_in = 2U;
    vlSelfRef.tb_FM_Index__DOT__pattern = 0x840000U;
    co_await vlSelfRef.__VdlySched.delay(0xaULL, nullptr, 
                                         "tb_FM_Index.sv", 
                                         45);
    vlSelfRef.tb_FM_Index__DOT__reset = 0U;
    vlSelfRef.tb_FM_Index__DOT__start = 1U;
    co_await vlSelfRef.__VdlySched.delay(0xaULL, nullptr, 
                                         "tb_FM_Index.sv", 
                                         50);
    vlSelfRef.tb_FM_Index__DOT__start = 0U;
    co_await vlSelfRef.__VdlySched.delay(0xc8ULL, nullptr, 
                                         "tb_FM_Index.sv", 
                                         54);
    VL_FINISH_MT("tb_FM_Index.sv", 54, "");
}

void Vtb_FM_Index___024root___eval_act(Vtb_FM_Index___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_FM_Index___024root___eval_act\n"); );
    Vtb_FM_Index__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
}

void Vtb_FM_Index___024root___nba_sequent__TOP__0(Vtb_FM_Index___024root* vlSelf);

void Vtb_FM_Index___024root___eval_nba(Vtb_FM_Index___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_FM_Index___024root___eval_nba\n"); );
    Vtb_FM_Index__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if ((1ULL & vlSelfRef.__VnbaTriggered.word(0U))) {
        Vtb_FM_Index___024root___nba_sequent__TOP__0(vlSelf);
        vlSelfRef.__Vm_traceActivity[1U] = 1U;
    }
}

VL_INLINE_OPT void Vtb_FM_Index___024root___nba_sequent__TOP__0(Vtb_FM_Index___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_FM_Index___024root___nba_sequent__TOP__0\n"); );
    Vtb_FM_Index__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Init
    CData/*3:0*/ __Vdly__tb_FM_Index__DOT__dut__DOT__state;
    __Vdly__tb_FM_Index__DOT__dut__DOT__state = 0;
    IData/*31:0*/ __Vdly__tb_FM_Index__DOT__dut__DOT__pat_idx;
    __Vdly__tb_FM_Index__DOT__dut__DOT__pat_idx = 0;
    CData/*3:0*/ __Vdly__tb_FM_Index__DOT__dut__DOT__l;
    __Vdly__tb_FM_Index__DOT__dut__DOT__l = 0;
    CData/*3:0*/ __Vdly__tb_FM_Index__DOT__dut__DOT__r;
    __Vdly__tb_FM_Index__DOT__dut__DOT__r = 0;
    // Body
    __Vdly__tb_FM_Index__DOT__dut__DOT__state = vlSelfRef.tb_FM_Index__DOT__dut__DOT__state;
    __Vdly__tb_FM_Index__DOT__dut__DOT__pat_idx = vlSelfRef.tb_FM_Index__DOT__dut__DOT__pat_idx;
    __Vdly__tb_FM_Index__DOT__dut__DOT__l = vlSelfRef.tb_FM_Index__DOT__dut__DOT__l;
    __Vdly__tb_FM_Index__DOT__dut__DOT__r = vlSelfRef.tb_FM_Index__DOT__dut__DOT__r;
    if (vlSelfRef.tb_FM_Index__DOT__reset) {
        __Vdly__tb_FM_Index__DOT__dut__DOT__state = 0U;
        vlSelfRef.tb_FM_Index__DOT__done = 0U;
        vlSelfRef.tb_FM_Index__DOT__fail = 0U;
    } else if ((8U & (IData)(vlSelfRef.tb_FM_Index__DOT__dut__DOT__state))) {
        if ((4U & (IData)(vlSelfRef.tb_FM_Index__DOT__dut__DOT__state))) {
            __Vdly__tb_FM_Index__DOT__dut__DOT__state = 0U;
        } else if ((2U & (IData)(vlSelfRef.tb_FM_Index__DOT__dut__DOT__state))) {
            __Vdly__tb_FM_Index__DOT__dut__DOT__state = 0U;
        } else if ((1U & (IData)(vlSelfRef.tb_FM_Index__DOT__dut__DOT__state))) {
            __Vdly__tb_FM_Index__DOT__dut__DOT__state = 0U;
        } else {
            vlSelfRef.tb_FM_Index__DOT__fail = 1U;
            __Vdly__tb_FM_Index__DOT__dut__DOT__state = 0U;
        }
    } else if ((4U & (IData)(vlSelfRef.tb_FM_Index__DOT__dut__DOT__state))) {
        if ((2U & (IData)(vlSelfRef.tb_FM_Index__DOT__dut__DOT__state))) {
            if ((1U & (IData)(vlSelfRef.tb_FM_Index__DOT__dut__DOT__state))) {
                vlSelfRef.tb_FM_Index__DOT__done = 1U;
                __Vdly__tb_FM_Index__DOT__dut__DOT__state = 0U;
            } else if (((IData)(vlSelfRef.tb_FM_Index__DOT__dut__DOT__l) 
                        >= (IData)(vlSelfRef.tb_FM_Index__DOT__dut__DOT__r))) {
                __Vdly__tb_FM_Index__DOT__dut__DOT__state = 8U;
            } else if ((0U == vlSelfRef.tb_FM_Index__DOT__dut__DOT__loop_count)) {
                __Vdly__tb_FM_Index__DOT__dut__DOT__state = 7U;
            } else {
                __Vdly__tb_FM_Index__DOT__dut__DOT__pat_idx 
                    = (vlSelfRef.tb_FM_Index__DOT__dut__DOT__pat_idx 
                       - (IData)(1U));
                __Vdly__tb_FM_Index__DOT__dut__DOT__state = 2U;
            }
        } else if ((1U & (IData)(vlSelfRef.tb_FM_Index__DOT__dut__DOT__state))) {
            __Vdly__tb_FM_Index__DOT__dut__DOT__l = 
                (0xfU & (((4U >= (IData)(vlSelfRef.tb_FM_Index__DOT__dut__DOT__c))
                           ? vlSelfRef.tb_FM_Index__DOT__dut__DOT__C_arr
                          [vlSelfRef.tb_FM_Index__DOT__dut__DOT__c]
                           : 0U) + (IData)(vlSelfRef.tb_FM_Index__DOT__dut__DOT__rank_l)));
            __Vdly__tb_FM_Index__DOT__dut__DOT__r = 
                (0xfU & (((4U >= (IData)(vlSelfRef.tb_FM_Index__DOT__dut__DOT__c))
                           ? vlSelfRef.tb_FM_Index__DOT__dut__DOT__C_arr
                          [vlSelfRef.tb_FM_Index__DOT__dut__DOT__c]
                           : 0U) + (IData)(vlSelfRef.tb_FM_Index__DOT__dut__DOT__rank_r)));
            __Vdly__tb_FM_Index__DOT__dut__DOT__state = 6U;
        } else {
            vlSelfRef.tb_FM_Index__DOT__dut__DOT__rank_r 
                = ((8U >= (IData)(vlSelfRef.tb_FM_Index__DOT__dut__DOT__r))
                    ? vlSelfRef.tb_FM_Index__DOT__dut__DOT__Occ
                   [((4U >= (IData)(vlSelfRef.tb_FM_Index__DOT__dut__DOT__c))
                      ? (IData)(vlSelfRef.tb_FM_Index__DOT__dut__DOT__c)
                      : 0U)][vlSelfRef.tb_FM_Index__DOT__dut__DOT__r]
                    : 0U);
            __Vdly__tb_FM_Index__DOT__dut__DOT__state = 5U;
        }
    } else if ((2U & (IData)(vlSelfRef.tb_FM_Index__DOT__dut__DOT__state))) {
        if ((1U & (IData)(vlSelfRef.tb_FM_Index__DOT__dut__DOT__state))) {
            vlSelfRef.tb_FM_Index__DOT__dut__DOT__rank_l 
                = ((8U >= (IData)(vlSelfRef.tb_FM_Index__DOT__dut__DOT__l))
                    ? vlSelfRef.tb_FM_Index__DOT__dut__DOT__Occ
                   [((4U >= (IData)(vlSelfRef.tb_FM_Index__DOT__dut__DOT__c))
                      ? (IData)(vlSelfRef.tb_FM_Index__DOT__dut__DOT__c)
                      : 0U)][vlSelfRef.tb_FM_Index__DOT__dut__DOT__l]
                    : 0U);
            __Vdly__tb_FM_Index__DOT__dut__DOT__state = 4U;
        } else {
            vlSelfRef.tb_FM_Index__DOT__dut__DOT__loop_count 
                = (vlSelfRef.tb_FM_Index__DOT__dut__DOT__loop_count 
                   - (IData)(1U));
            vlSelfRef.tb_FM_Index__DOT__dut__DOT__c 
                = ((0x17U >= (0x1fU & VL_MULS_III(32, (IData)(3U), vlSelfRef.tb_FM_Index__DOT__dut__DOT__pat_idx)))
                    ? (7U & (vlSelfRef.tb_FM_Index__DOT__pattern 
                             >> (0x1fU & VL_MULS_III(32, (IData)(3U), vlSelfRef.tb_FM_Index__DOT__dut__DOT__pat_idx))))
                    : 0U);
            __Vdly__tb_FM_Index__DOT__dut__DOT__state = 3U;
        }
    } else if ((1U & (IData)(vlSelfRef.tb_FM_Index__DOT__dut__DOT__state))) {
        __Vdly__tb_FM_Index__DOT__dut__DOT__pat_idx = 7U;
        __Vdly__tb_FM_Index__DOT__dut__DOT__l = 0U;
        __Vdly__tb_FM_Index__DOT__dut__DOT__r = 8U;
        __Vdly__tb_FM_Index__DOT__dut__DOT__state = 2U;
    } else {
        vlSelfRef.tb_FM_Index__DOT__dut__DOT__loop_count 
            = vlSelfRef.tb_FM_Index__DOT__pat_len_in;
        vlSelfRef.tb_FM_Index__DOT__done = 0U;
        vlSelfRef.tb_FM_Index__DOT__fail = 0U;
        if (vlSelfRef.tb_FM_Index__DOT__start) {
            __Vdly__tb_FM_Index__DOT__dut__DOT__state = 1U;
        }
    }
    vlSelfRef.tb_FM_Index__DOT__dut__DOT__state = __Vdly__tb_FM_Index__DOT__dut__DOT__state;
    vlSelfRef.tb_FM_Index__DOT__dut__DOT__pat_idx = __Vdly__tb_FM_Index__DOT__dut__DOT__pat_idx;
    vlSelfRef.tb_FM_Index__DOT__dut__DOT__l = __Vdly__tb_FM_Index__DOT__dut__DOT__l;
    vlSelfRef.tb_FM_Index__DOT__dut__DOT__r = __Vdly__tb_FM_Index__DOT__dut__DOT__r;
}

void Vtb_FM_Index___024root___timing_resume(Vtb_FM_Index___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_FM_Index___024root___timing_resume\n"); );
    Vtb_FM_Index__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if ((2ULL & vlSelfRef.__VactTriggered.word(0U))) {
        vlSelfRef.__VdlySched.resume();
    }
}

void Vtb_FM_Index___024root___eval_triggers__act(Vtb_FM_Index___024root* vlSelf);

bool Vtb_FM_Index___024root___eval_phase__act(Vtb_FM_Index___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_FM_Index___024root___eval_phase__act\n"); );
    Vtb_FM_Index__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Init
    VlTriggerVec<2> __VpreTriggered;
    CData/*0:0*/ __VactExecute;
    // Body
    Vtb_FM_Index___024root___eval_triggers__act(vlSelf);
    __VactExecute = vlSelfRef.__VactTriggered.any();
    if (__VactExecute) {
        __VpreTriggered.andNot(vlSelfRef.__VactTriggered, vlSelfRef.__VnbaTriggered);
        vlSelfRef.__VnbaTriggered.thisOr(vlSelfRef.__VactTriggered);
        Vtb_FM_Index___024root___timing_resume(vlSelf);
        Vtb_FM_Index___024root___eval_act(vlSelf);
    }
    return (__VactExecute);
}

bool Vtb_FM_Index___024root___eval_phase__nba(Vtb_FM_Index___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_FM_Index___024root___eval_phase__nba\n"); );
    Vtb_FM_Index__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Init
    CData/*0:0*/ __VnbaExecute;
    // Body
    __VnbaExecute = vlSelfRef.__VnbaTriggered.any();
    if (__VnbaExecute) {
        Vtb_FM_Index___024root___eval_nba(vlSelf);
        vlSelfRef.__VnbaTriggered.clear();
    }
    return (__VnbaExecute);
}

#ifdef VL_DEBUG
VL_ATTR_COLD void Vtb_FM_Index___024root___dump_triggers__nba(Vtb_FM_Index___024root* vlSelf);
#endif  // VL_DEBUG
#ifdef VL_DEBUG
VL_ATTR_COLD void Vtb_FM_Index___024root___dump_triggers__act(Vtb_FM_Index___024root* vlSelf);
#endif  // VL_DEBUG

void Vtb_FM_Index___024root___eval(Vtb_FM_Index___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_FM_Index___024root___eval\n"); );
    Vtb_FM_Index__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Init
    IData/*31:0*/ __VnbaIterCount;
    CData/*0:0*/ __VnbaContinue;
    // Body
    __VnbaIterCount = 0U;
    __VnbaContinue = 1U;
    while (__VnbaContinue) {
        if (VL_UNLIKELY(((0x64U < __VnbaIterCount)))) {
#ifdef VL_DEBUG
            Vtb_FM_Index___024root___dump_triggers__nba(vlSelf);
#endif
            VL_FATAL_MT("tb_FM_Index.sv", 7, "", "NBA region did not converge.");
        }
        __VnbaIterCount = ((IData)(1U) + __VnbaIterCount);
        __VnbaContinue = 0U;
        vlSelfRef.__VactIterCount = 0U;
        vlSelfRef.__VactContinue = 1U;
        while (vlSelfRef.__VactContinue) {
            if (VL_UNLIKELY(((0x64U < vlSelfRef.__VactIterCount)))) {
#ifdef VL_DEBUG
                Vtb_FM_Index___024root___dump_triggers__act(vlSelf);
#endif
                VL_FATAL_MT("tb_FM_Index.sv", 7, "", "Active region did not converge.");
            }
            vlSelfRef.__VactIterCount = ((IData)(1U) 
                                         + vlSelfRef.__VactIterCount);
            vlSelfRef.__VactContinue = 0U;
            if (Vtb_FM_Index___024root___eval_phase__act(vlSelf)) {
                vlSelfRef.__VactContinue = 1U;
            }
        }
        if (Vtb_FM_Index___024root___eval_phase__nba(vlSelf)) {
            __VnbaContinue = 1U;
        }
    }
}

#ifdef VL_DEBUG
void Vtb_FM_Index___024root___eval_debug_assertions(Vtb_FM_Index___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_FM_Index___024root___eval_debug_assertions\n"); );
    Vtb_FM_Index__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
}
#endif  // VL_DEBUG
