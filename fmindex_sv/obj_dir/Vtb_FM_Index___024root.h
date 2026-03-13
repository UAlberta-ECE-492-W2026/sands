// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design internal header
// See Vtb_FM_Index.h for the primary calling header

#ifndef VERILATED_VTB_FM_INDEX___024ROOT_H_
#define VERILATED_VTB_FM_INDEX___024ROOT_H_  // guard

#include "verilated.h"
#include "verilated_timing.h"


class Vtb_FM_Index__Syms;

class alignas(VL_CACHE_LINE_BYTES) Vtb_FM_Index___024root final : public VerilatedModule {
  public:

    // DESIGN SPECIFIC STATE
    CData/*0:0*/ tb_FM_Index__DOT__clk;
    CData/*0:0*/ tb_FM_Index__DOT__reset;
    CData/*0:0*/ tb_FM_Index__DOT__start;
    CData/*0:0*/ tb_FM_Index__DOT__done;
    CData/*0:0*/ tb_FM_Index__DOT__fail;
    CData/*3:0*/ tb_FM_Index__DOT__dut__DOT__state;
    CData/*3:0*/ tb_FM_Index__DOT__dut__DOT__l;
    CData/*3:0*/ tb_FM_Index__DOT__dut__DOT__r;
    CData/*3:0*/ tb_FM_Index__DOT__dut__DOT__rank_l;
    CData/*3:0*/ tb_FM_Index__DOT__dut__DOT__rank_r;
    CData/*2:0*/ tb_FM_Index__DOT__dut__DOT__c;
    CData/*0:0*/ __Vtrigprevexpr___TOP__tb_FM_Index__DOT__clk__0;
    CData/*0:0*/ __VactContinue;
    IData/*23:0*/ tb_FM_Index__DOT__pattern;
    IData/*31:0*/ tb_FM_Index__DOT__pat_len_in;
    IData/*31:0*/ tb_FM_Index__DOT__dut__DOT__pat_idx;
    IData/*31:0*/ tb_FM_Index__DOT__dut__DOT__loop_count;
    IData/*31:0*/ __VactIterCount;
    VlUnpacked<CData/*3:0*/, 5> tb_FM_Index__DOT__dut__DOT__C_arr;
    VlUnpacked<VlUnpacked<CData/*3:0*/, 9>, 5> tb_FM_Index__DOT__dut__DOT__Occ;
    VlUnpacked<CData/*0:0*/, 2> __Vm_traceActivity;
    VlDelayScheduler __VdlySched;
    VlTriggerVec<2> __VactTriggered;
    VlTriggerVec<2> __VnbaTriggered;

    // INTERNAL VARIABLES
    Vtb_FM_Index__Syms* const vlSymsp;

    // CONSTRUCTORS
    Vtb_FM_Index___024root(Vtb_FM_Index__Syms* symsp, const char* v__name);
    ~Vtb_FM_Index___024root();
    VL_UNCOPYABLE(Vtb_FM_Index___024root);

    // INTERNAL METHODS
    void __Vconfigure(bool first);
};


#endif  // guard
