// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Tracing implementation internals
#include "verilated_vcd_c.h"
#include "Vtb_FM_Index__Syms.h"


VL_ATTR_COLD void Vtb_FM_Index___024root__trace_init_sub__TOP__0(Vtb_FM_Index___024root* vlSelf, VerilatedVcd* tracep) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_FM_Index___024root__trace_init_sub__TOP__0\n"); );
    Vtb_FM_Index__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Init
    const int c = vlSymsp->__Vm_baseCode;
    // Body
    tracep->pushPrefix("tb_FM_Index", VerilatedTracePrefixType::SCOPE_MODULE);
    tracep->declBit(c+16,0,"clk",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+17,0,"reset",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+18,0,"start",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+19,0,"pattern",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 23,0);
    tracep->declBus(c+20,0,"pat_len_in",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::INT, false,-1, 31,0);
    tracep->declBit(c+6,0,"done",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+7,0,"fail",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+8,0,"l_out",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 3,0);
    tracep->declBus(c+9,0,"r_out",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 3,0);
    tracep->pushPrefix("dut", VerilatedTracePrefixType::SCOPE_MODULE);
    tracep->declBit(c+16,0,"clk",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+17,0,"reset",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+18,0,"start",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+19,0,"pattern",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 23,0);
    tracep->declBus(c+20,0,"pat_len_in",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::INT, false,-1, 31,0);
    tracep->declBit(c+6,0,"done",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+7,0,"fail",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+8,0,"l_out",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 3,0);
    tracep->declBus(c+9,0,"r_out",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 3,0);
    tracep->declBus(c+10,0,"state",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 3,0);
    tracep->declBus(c+8,0,"l",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 3,0);
    tracep->declBus(c+9,0,"r",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 3,0);
    tracep->declBus(c+11,0,"rank_l",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 3,0);
    tracep->declBus(c+12,0,"rank_r",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 3,0);
    tracep->declBus(c+13,0,"c",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 2,0);
    tracep->declBus(c+14,0,"pat_idx",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::INT, false,-1, 31,0);
    tracep->declBus(c+15,0,"loop_count",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::INT, false,-1, 31,0);
    tracep->pushPrefix("C_arr", VerilatedTracePrefixType::ARRAY_UNPACKED);
    for (int i = 0; i < 5; ++i) {
        tracep->declBus(c+1+i*1,0,"",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, true,(i+0), 3,0);
    }
    tracep->popPrefix();
    tracep->popPrefix();
    tracep->popPrefix();
}

VL_ATTR_COLD void Vtb_FM_Index___024root__trace_init_top(Vtb_FM_Index___024root* vlSelf, VerilatedVcd* tracep) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_FM_Index___024root__trace_init_top\n"); );
    Vtb_FM_Index__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    Vtb_FM_Index___024root__trace_init_sub__TOP__0(vlSelf, tracep);
}

VL_ATTR_COLD void Vtb_FM_Index___024root__trace_const_0(void* voidSelf, VerilatedVcd::Buffer* bufp);
VL_ATTR_COLD void Vtb_FM_Index___024root__trace_full_0(void* voidSelf, VerilatedVcd::Buffer* bufp);
void Vtb_FM_Index___024root__trace_chg_0(void* voidSelf, VerilatedVcd::Buffer* bufp);
void Vtb_FM_Index___024root__trace_cleanup(void* voidSelf, VerilatedVcd* /*unused*/);

VL_ATTR_COLD void Vtb_FM_Index___024root__trace_register(Vtb_FM_Index___024root* vlSelf, VerilatedVcd* tracep) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_FM_Index___024root__trace_register\n"); );
    Vtb_FM_Index__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    tracep->addConstCb(&Vtb_FM_Index___024root__trace_const_0, 0U, vlSelf);
    tracep->addFullCb(&Vtb_FM_Index___024root__trace_full_0, 0U, vlSelf);
    tracep->addChgCb(&Vtb_FM_Index___024root__trace_chg_0, 0U, vlSelf);
    tracep->addCleanupCb(&Vtb_FM_Index___024root__trace_cleanup, vlSelf);
}

VL_ATTR_COLD void Vtb_FM_Index___024root__trace_const_0(void* voidSelf, VerilatedVcd::Buffer* bufp) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_FM_Index___024root__trace_const_0\n"); );
    // Init
    Vtb_FM_Index___024root* const __restrict vlSelf VL_ATTR_UNUSED = static_cast<Vtb_FM_Index___024root*>(voidSelf);
    Vtb_FM_Index__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
}

VL_ATTR_COLD void Vtb_FM_Index___024root__trace_full_0_sub_0(Vtb_FM_Index___024root* vlSelf, VerilatedVcd::Buffer* bufp);

VL_ATTR_COLD void Vtb_FM_Index___024root__trace_full_0(void* voidSelf, VerilatedVcd::Buffer* bufp) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_FM_Index___024root__trace_full_0\n"); );
    // Init
    Vtb_FM_Index___024root* const __restrict vlSelf VL_ATTR_UNUSED = static_cast<Vtb_FM_Index___024root*>(voidSelf);
    Vtb_FM_Index__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    // Body
    Vtb_FM_Index___024root__trace_full_0_sub_0((&vlSymsp->TOP), bufp);
}

VL_ATTR_COLD void Vtb_FM_Index___024root__trace_full_0_sub_0(Vtb_FM_Index___024root* vlSelf, VerilatedVcd::Buffer* bufp) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtb_FM_Index___024root__trace_full_0_sub_0\n"); );
    Vtb_FM_Index__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Init
    uint32_t* const oldp VL_ATTR_UNUSED = bufp->oldp(vlSymsp->__Vm_baseCode);
    // Body
    bufp->fullCData(oldp+1,(vlSelfRef.tb_FM_Index__DOT__dut__DOT__C_arr[0]),4);
    bufp->fullCData(oldp+2,(vlSelfRef.tb_FM_Index__DOT__dut__DOT__C_arr[1]),4);
    bufp->fullCData(oldp+3,(vlSelfRef.tb_FM_Index__DOT__dut__DOT__C_arr[2]),4);
    bufp->fullCData(oldp+4,(vlSelfRef.tb_FM_Index__DOT__dut__DOT__C_arr[3]),4);
    bufp->fullCData(oldp+5,(vlSelfRef.tb_FM_Index__DOT__dut__DOT__C_arr[4]),4);
    bufp->fullBit(oldp+6,(vlSelfRef.tb_FM_Index__DOT__done));
    bufp->fullBit(oldp+7,(vlSelfRef.tb_FM_Index__DOT__fail));
    bufp->fullCData(oldp+8,(vlSelfRef.tb_FM_Index__DOT__dut__DOT__l),4);
    bufp->fullCData(oldp+9,(vlSelfRef.tb_FM_Index__DOT__dut__DOT__r),4);
    bufp->fullCData(oldp+10,(vlSelfRef.tb_FM_Index__DOT__dut__DOT__state),4);
    bufp->fullCData(oldp+11,(vlSelfRef.tb_FM_Index__DOT__dut__DOT__rank_l),4);
    bufp->fullCData(oldp+12,(vlSelfRef.tb_FM_Index__DOT__dut__DOT__rank_r),4);
    bufp->fullCData(oldp+13,(vlSelfRef.tb_FM_Index__DOT__dut__DOT__c),3);
    bufp->fullIData(oldp+14,(vlSelfRef.tb_FM_Index__DOT__dut__DOT__pat_idx),32);
    bufp->fullIData(oldp+15,(vlSelfRef.tb_FM_Index__DOT__dut__DOT__loop_count),32);
    bufp->fullBit(oldp+16,(vlSelfRef.tb_FM_Index__DOT__clk));
    bufp->fullBit(oldp+17,(vlSelfRef.tb_FM_Index__DOT__reset));
    bufp->fullBit(oldp+18,(vlSelfRef.tb_FM_Index__DOT__start));
    bufp->fullIData(oldp+19,(vlSelfRef.tb_FM_Index__DOT__pattern),24);
    bufp->fullIData(oldp+20,(vlSelfRef.tb_FM_Index__DOT__pat_len_in),32);
}
