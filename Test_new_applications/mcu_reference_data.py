"""
Reference MCU physical/process/power data, organized by manufacturer and
usage class (ULP / low-cost / high-performance), for use in selecting an
ASI reference-scenario baseline.

IMPORTANT CAVEATS (read before using these numbers in your model):

1. DIE SIZE is not publicly disclosed by any vendor for any part below,
   despite a further search attempt (teardown/die-photo reports such as
   TechInsights are paywalled and were not accessible). die_size_mm2 is
   None everywhere. Use wlcsp_area_mm2 as the best available proxy: WLCSP
   is wafer-level (no separate substrate/leadframe), so package size is
   close to true die size, typically a slight overestimate due to bump
   pad routing / scribe margin.

2. PROCESS NODE is confirmed for STMicroelectronics (community + press
   sources), Nordic (press releases, CEO statements), NXP Kinetis KL0x
   (90nm Thin-Film-Storage, NXP datasheet/fact sheet), Silicon Labs
   EFR32 Series 2 (40nm, multiple product pages), and Ambiq Apollo3
   Blue (TSMC 40ULP, confirmed via a TSMC press release rather than the
   Ambiq datasheet itself). It is genuinely NOT disclosed in public
   material for Microchip/SAM, Ambiq Apollo4+, Texas Instruments,
   remaining NXP parts, remaining Silicon Labs parts, onsemi RSL10,
   Renesas/Dialog, or Infineon/Cypress parts below -- these vendors
   simply do not publish it, this is not a gap in the search.

3. RUN MODE CURRENT (uA/MHz) and SLEEP MODE CURRENT are datasheet/vendor
   typical figures. These are NOT directly comparable across vendors
   without care:
     - Different vendors measure at different voltages, temperatures, and
       with different peripheral/cache/regulator states (e.g. ST figures
       are "peripherals off"; Nordic figures depend on LDO vs DCDC mode;
       Dialog/Renesas DA14531 depends on VBAT_LOW/boost vs VBAT_HIGH/buck
       regulator mode; Infineon PSoC 6 depends on core logic voltage
       (1.1V vs 0.9V ULP) -- both/all modes are noted where found, and
       the LOWER (regulator-optimized / vendor-recommended) figure is
       reported as the primary run_uA_per_MHz value).
     - "Sleep" is not a standardized term across vendors: it can mean
       CPU-clock-gated-only (fast wake, higher current), a retention
       sleep state with SRAM kept (e.g. Nordic System ON idle, EFx EM2),
       or a full deep-sleep/standby/hibernate state with little or no
       retention (slow wake, lowest current, e.g. Nordic System OFF,
       STM32 Standby, RSL10 Deep Sleep, DA14531 Hibernation). Where a
       vendor offers multiple depths, this table reports the deepest
       state that still has a clearly documented current figure -- see
       source_note per entry for exactly what was measured and what
       shallower/deeper alternatives exist.
     - A few parts (onsemi RSL10) do not publish a uA/MHz run-mode figure
       at all, only a CoreMark/mA efficiency metric -- run_uA_per_MHz is
       None for those, see source_note.
     - Always re-verify against the specific datasheet before using in a
       publication; these are typical/representative values transcribed
       from public datasheet/press material, not a substitute for the
       primary source. Several figures below are flagged in source_note
       as "approximate" or "not independently table-verified" where the
       research pass could only extract a search-summarized figure
       rather than read the exact datasheet table row -- treat those
       with extra caution.

4. USAGE CLASS is collapsed to three buckets (ULP / Low-cost /
   High-performance) per the vendor's own marketing positioning and
   typical core/clock tier, even for wireless SoCs (a BLE radio SoC
   built around a Cortex-M0+/M3/M4 aimed at coin-cell operation is
   classed ULP; one built around a Cortex-M33 aimed at Matter/Thread
   gateway-class throughput is classed High-performance). This is a
   simplification -- real parts sit on a continuum -- but keeps the
   table and plots consistent across ~15 vendors.

5. All dimensions in mm, area in mm^2, process node in nm, current in uA.

6. Last updated 2026-07-29: expanded from the original 4-vendor pass
   (STMicroelectronics, Nordic, Microchip, Ambiq) to add Texas
   Instruments, NXP, Silicon Labs, onsemi, Renesas (incl. the former
   Dialog Semiconductor BLE line), and Infineon/Cypress, and to fill
   several previously-None fields in the original 4 vendors using
   direct datasheet pulls. Parts confirmed to NOT offer a WLCSP package
   option (e.g. NXP Kinetis KE0x, Silicon Labs EFM32GG/TG, Renesas
   RA4W1/Synergy/DA1469x, Renesas RE01 which uses "WLBGA" not WLCSP)
   were deliberately excluded rather than included with null package
   data.
"""


import matplotlib.pyplot as plt

MCU_DATA = [
    # ------------------------------------------------------------------
    # STMicroelectronics
    # ------------------------------------------------------------------
    {
        "manufacturer": "STMicroelectronics",
        "mcu_name": "STM32L011E4",
        "usage_class": "ULP",
        "core": "Cortex-M0+",
        "wlcsp_size_mm": (2.133, 2.070),
        "wlcsp_area_mm2": 4.42,
        "die_size_mm2": None,
        "process_node_nm": 90,
        "run_uA_per_MHz": 130,
        "sleep_current_uA": 0.23,  # Standby, no RTC, VDD=3.0V
        "source_note": "WLCSP25 dims from STM32L011x3/x4 datasheet mechanical "
                        "data table (D4/E4 share the same die). Run mode: two "
                        "independent extractions gave 128 and 138 uA/MHz for "
                        "Range 1 (HSI16, code from Flash) -- reported as ~130 "
                        "uA/MHz, treat as approximate pending a manual table "
                        "check. Standby: 0.23 uA (no RTC) / 0.67 uA (with RTC), "
                        "VDD=3.0V. Stop mode 0.29-0.54 uA depending on RTC/RAM "
                        "retention. Source: st.com/resource/en/datasheet/"
                        "stm32l011d4.pdf",
    },
    {
        "manufacturer": "STMicroelectronics",
        "mcu_name": "STM32L031x4/x6",
        "usage_class": "ULP",
        "core": "Cortex-M0+",
        "wlcsp_size_mm": None,
        "wlcsp_area_mm2": None,
        "die_size_mm2": None,
        "process_node_nm": 90,
        "run_uA_per_MHz": 76,
        "sleep_current_uA": 0.23,  # Standby mode, 2 wakeup pins
        "source_note": "Datasheet: 76 uA/MHz Run mode; 0.23 uA Standby (2 wakeup "
                        "pins); 0.35 uA Stop mode (16 wakeup lines); 0.6 uA Stop "
                        "+ RTC + 8KB RAM retention. sleep_current_uA reported "
                        "here is Standby (deepest retained state), not Sleep-mode "
                        "proper -- see notes above on terminology.",
    },
    {
        "manufacturer": "STMicroelectronics",
        "mcu_name": "STM32L051x6/x8",
        "usage_class": "ULP",
        "core": "Cortex-M0+",
        "wlcsp_size_mm": (2.61, 2.88),
        "wlcsp_area_mm2": 7.52,
        "die_size_mm2": None,
        "process_node_nm": 90,
        "run_uA_per_MHz": 140,
        "sleep_current_uA": 0.28,  # Standby, no RTC
        "source_note": "Run mode varies by voltage/frequency range: Range 1 "
                        "~140 uA/MHz, Range 2 ~88 uA/MHz, Range 3 ~37 uA/MHz "
                        "(all code from Flash) -- Range 1 (highest perf) "
                        "reported here. Standby 0.28-0.29 uA (no RTC), 0.65-0.85 "
                        "uA (with RTC); Stop 0.4-1.0 uA. WLCSP ball count "
                        "extracted this pass as \"WLCSP36\", which conflicts "
                        "with the original WLCSP49 figure -- flagged as a "
                        "possible OCR misread, dims (2.61x2.88mm) themselves "
                        "were re-confirmed. Source: st.com/resource/en/"
                        "datasheet/stm32l051c6.pdf",
    },
    {
        "manufacturer": "STMicroelectronics",
        "mcu_name": "STM32L451xx",
        "usage_class": "ULP",
        "core": "Cortex-M4F",
        "wlcsp_size_mm": (3.36, 3.66),
        "wlcsp_area_mm2": 12.30,
        "die_size_mm2": None,
        "process_node_nm": 90,
        "run_uA_per_MHz": 84,
        "sleep_current_uA": 2.05,  # Stop 2 mode typical
        "source_note": "Datasheet: 84 uA/MHz Run mode (executing from flash); "
                        "Stop 2 mode typical 2.05 uA (best wake-time/power "
                        "trade-off of the Stop modes, SRAM/register retention).",
    },
    {
        "manufacturer": "STMicroelectronics",
        "mcu_name": "STM32C011/STM32C031 (STM32C0 series)",
        "usage_class": "Low-cost",
        "core": "Cortex-M0+",
        "wlcsp_size_mm": (1.70, 1.42),
        "wlcsp_area_mm2": 2.41,
        "die_size_mm2": None,
        "process_node_nm": 90,
        "run_uA_per_MHz": 80,
        "sleep_current_uA": 8,  # Standby mode typical
        "source_note": "ST product overview: RUN at 48 MHz = 80 uA/MHz "
                        "(2.7 us wakeup); STOP = 80 uA absolute, 23 us wakeup; "
                        "STANDBY = 8 uA absolute. sleep_current_uA given here "
                        "is STANDBY (deepest state); STOP mode is 80 uA (not "
                        "per-MHz -- an absolute current, since clock is halted).",
    },
    {
        "manufacturer": "STMicroelectronics",
        "mcu_name": "STM32G0 series (Value line)",
        "usage_class": "Low-cost",
        "core": "Cortex-M0+",
        "wlcsp_size_mm": (1.86, 2.14),
        "wlcsp_area_mm2": 3.98,
        "die_size_mm2": None,
        "process_node_nm": 90,
        "run_uA_per_MHz": 85,
        "sleep_current_uA": 0.4,
        "source_note": "Smallest WLCSP offered: WLCSP18, 1.86x2.14mm (package "
                        "marking B06E) on STM32G031. Process node 90nm "
                        "confirmed via ST's own blog, \"STM32G0: 1st Mainstream "
                        "90nm MCU\" (blog.st.com/stm32g0-mainstream-90-nm-mcu), "
                        "explicitly contrasted with STM32F0's 180nm. Run mode "
                        "~80-90 uA/MHz at VDD=3.0V/64MHz and Standby ~0.3-0.5 "
                        "uA (Stop0 ~2-3uA, Stop1 ~1-2uA) are approximate -- "
                        "table extraction wasn't clean, re-check "
                        "st.com/resource/en/datasheet/stm32g031c6.pdf directly "
                        "before publication use.",
    },
   # {
   #     "manufacturer": "STMicroelectronics",
   #     "mcu_name": "STM32H7x7 (dual-core H747/H757)",
   #     "usage_class": "High-performance",
   #     "core": "Cortex-M7 + Cortex-M4",
   #     "wlcsp_size_mm": (4.96, 4.64),
   #     "wlcsp_area_mm2": 23.01,
   #     "die_size_mm2": None,
   #     "process_node_nm": 40,
   #     "run_uA_per_MHz": 278,
   #     "sleep_current_uA": 7,  # Standby mode, low-power
   #     "source_note": "ST product page: 278 uA/MHz typical @3.3V/25C in Run "
   #                     "mode (peripherals off); 7 uA Standby (low-power mode). "
   #                     "Earlier press material for the original STM32H743 "
   #                     "quoted <280 uA/MHz run / <7 uA standby -- consistent.",
   # },
    {
        "manufacturer": "STMicroelectronics",
        "mcu_name": "STM32F745/F746/F756",
        "usage_class": "High-performance",
        "core": "Cortex-M7",
        "wlcsp_size_mm": (4.54, 5.85),
        "wlcsp_area_mm2": 26.55,
        "die_size_mm2": None,
        "process_node_nm": 90,
        "run_uA_per_MHz": None,
        "sleep_current_uA": None,
        "source_note": "WLCSP availability is mixed across the F7 line: "
                        "STM32F730/72x/73x are confirmed NOT offered in WLCSP "
                        "(LQFP/UFBGA only, per stm32f730i8.pdf), while "
                        "F745/F746/F756 ARE offered in WLCSP143, dims here "
                        "extracted as ~4.539x5.849mm (last-digit precision "
                        "approximate). F765/76x/77x reportedly get WLCSP180 "
                        "but dims not independently confirmed. Process node "
                        "90nm inferred from ST's STM32H7 blog post which "
                        "describes H7's 40nm as a shrink *from* F7's 90nm "
                        "(blog.st.com/stm32h7-powerful-cortex-m7-coremark). "
                        "Run/sleep current not found: the datasheet gives only "
                        "absolute mA figures per frequency/config, no "
                        "per-MHz-normalized table entry was extractable. "
                        "Source: st.com/resource/en/datasheet/stm32f745ie.pdf",
    },
    {
        "manufacturer": "STMicroelectronics",
        "mcu_name": "STM32U031 (U0 series)",
        "usage_class": "ULP",
        "core": "Cortex-M0+",
        "wlcsp_size_mm": (2.55, 2.34),
        "wlcsp_area_mm2": 5.97,
        "die_size_mm2": None,
        "process_node_nm": None,
        "run_uA_per_MHz": 78,
        "sleep_current_uA": 0.03,  # Standby, no RTC
        "source_note": "WLCSP27, 2.55x2.34mm. Run mode ~78 uA/MHz (Range1, "
                        "derived from 3.75mA @48MHz). Standby (no RTC) 30 nA, "
                        "Standby (with RTC) 160 nA; Stop2 515-630 nA; Shutdown "
                        "(deepest, no retention) 16 nA. Process node not "
                        "disclosed in datasheet text pulled. Source: st.com/"
                        "resource/en/datasheet/stm32u031c6.pdf",
    },
    {
        "manufacturer": "STMicroelectronics",
        "mcu_name": "STM32U575 (U5 series)",
        "usage_class": "ULP",
        "core": "Cortex-M33",
        "wlcsp_size_mm": (4.2, 3.95),
        "wlcsp_area_mm2": 16.59,
        "die_size_mm2": None,
        "process_node_nm": 40,
        "run_uA_per_MHz": 19.5,
        "sleep_current_uA": 0.21,  # Standby, 24 wake pins
        "source_note": "WLCSP90, 4.2x3.95mm. Run mode 19.5 uA/MHz @3.3V -- "
                        "notably the lowest active-power figure of any ARM "
                        "Cortex part in this table, reflecting the U5's "
                        "ultra-low-power positioning. Stop2 4.0-8.95 uA "
                        "(16KB-full SRAM retained), Stop3 1.9-4.3 uA, Standby "
                        "210 nA (24 wake pins). Process node not disclosed. "
                        "Source: st.com/resource/en/datasheet/stm32u575ai.pdf",
    },

    # ------------------------------------------------------------------
    # Nordic Semiconductor (wireless MCU/SoC -- radio+MCU combined die)
    # ------------------------------------------------------------------
    {
        "manufacturer": "Nordic Semiconductor",
        "mcu_name": "nRF52805",
        "usage_class": "ULP",
        "core": "Cortex-M4",
        "wlcsp_size_mm": (2.48, 2.46),
        "wlcsp_area_mm2": 6.10,
        "die_size_mm2": None,
        "process_node_nm": 55,
        "run_uA_per_MHz": None,
        "sleep_current_uA": 0.3,
        "source_note": "WLCSP dims from Nordic product brief, TSMC 55ULP "
                        "process. Run current not confirmed specifically for "
                        "this part; System OFF current (0.3 uA) taken from "
                        "nRF52832 (same nRF52 platform/process) as proxy.",
    },
    {
        "manufacturer": "Nordic Semiconductor",
        "mcu_name": "nRF52811",
        "usage_class": "ULP",
        "core": "Cortex-M4",
        "wlcsp_size_mm": (2.48, 2.46),
        "wlcsp_area_mm2": 6.10,
        "die_size_mm2": None,
        "process_node_nm": 55,
        "run_uA_per_MHz": None,
        "sleep_current_uA": 0.3,
        "source_note": "Same platform/process/package as nRF52805. Run current "
                        "not confirmed specifically; System OFF proxy from "
                        "nRF52832 (same nRF52 family).",
    },
    {
        "manufacturer": "Nordic Semiconductor",
        "mcu_name": "nRF52832",
        "usage_class": "ULP",
        "core": "Cortex-M4",
        "wlcsp_size_mm": None,
        "wlcsp_area_mm2": None,
        "die_size_mm2": None,
        "process_node_nm": 55,
        "run_uA_per_MHz": 61,
        "sleep_current_uA": 0.3,
        "source_note": "Run current from Nordic DevZone community-confirmed "
                        "datasheet figures: CPU running from flash, cache "
                        "disabled = 3.9 mA (DCDC regulator mode) or 8.0 mA "
                        "(LDO mode) @ 64 MHz -> 61 uA/MHz (DCDC) or 125 uA/MHz "
                        "(LDO). Reported figure uses DCDC (lower, and the "
                        "vendor-recommended mode). System OFF = 0.3 uA "
                        "(community-confirmed, matches datasheet).",
    },
    {
        "manufacturer": "Nordic Semiconductor",
        "mcu_name": "nRF52840",
        "usage_class": "ULP",
        "core": "Cortex-M4",
        "wlcsp_size_mm": (3.544, 3.607),
        "wlcsp_area_mm2": 12.78,
        "die_size_mm2": None,
        "process_node_nm": 55,
        "run_uA_per_MHz": 51.6,
        "sleep_current_uA": 0.4,  # System OFF, no RAM retention
        "source_note": "Confirmed directly from the nRF52840 Product "
                        "Specification current-consumption table: ICPU0 = 3.3 "
                        "mA typical for CoreMark @64MHz from flash, HFXO clock, "
                        "DC/DC regulator -> 51.6 uA/MHz. Other rows: ICPU1 "
                        "(LDO instead of DC/DC) 6.3mA (~98 uA/MHz); ICPU2 (from "
                        "RAM, DC/DC) 2.8mA (~43.8 uA/MHz); ICPU4 (HFINT clock, "
                        "DC/DC) 3.1mA (~48.4 uA/MHz). System OFF = 0.4 uA at "
                        "3V, no RAM retention. Source: docs.nordicsemi.com "
                        "nRF52840 Product Specification, current parameters "
                        "page (high-confidence, actual table read).",
    },
    {
        "manufacturer": "Nordic Semiconductor",
        "mcu_name": "nRF54L15",
        "usage_class": "ULP",
        "core": "Cortex-M33 (+ RISC-V coprocessor)",
        "wlcsp_size_mm": (2.4, 2.2),
        "wlcsp_area_mm2": 5.28,
        "die_size_mm2": None,
        "process_node_nm": 22,
        "run_uA_per_MHz": 20,
        "sleep_current_uA": 0.75,
        "source_note": "LOW CONFIDENCE, not table-verified: active current "
                        "~2.6 mA typical (CoreMark from RRAM with cache) at "
                        "128MHz max clock implies ~20 uA/MHz, and System OFF "
                        "sources disagreed in a 0.6-0.9 uA range (0.75 uA "
                        "midpoint reported) depending on wakeup/GRTC config. "
                        "Nordic's docs site (docs.nordicsemi.com/bundle/"
                        "ps_nrf54l15/page/pmu.html and cpu.html) requires a "
                        "JS-capable fetch that wasn't available this pass -- "
                        "recommend pulling those pages directly (or the "
                        "Mouser-hosted PDF) before using these two figures in "
                        "a publication. Process: TSMC 22ULL/GlobalFoundries "
                        "22FDX (vendor press materials).",
    },

    # ------------------------------------------------------------------
    # Microchip / Atmel
    # ------------------------------------------------------------------
    {
        "manufacturer": "Microchip (Atmel)",
        "mcu_name": "SAMD11",
        "usage_class": "ULP / Low-cost",
        "core": "Cortex-M0+",
        "wlcsp_size_mm": (2.43, 1.93),
        "wlcsp_area_mm2": 4.69,
        "die_size_mm2": None,
        "process_node_nm": None,
        "run_uA_per_MHz": None,
        "sleep_current_uA": None,
        "source_note": "WLCSP confirmed 20-ball, 2.43x1.93mm (Digi-Key listing "
                        "for ATSAMD11D14A-UUT). Active/standby current and "
                        "process node not found: the summary datasheet defers "
                        "electrical characteristics to the full datasheet, and "
                        "the full datasheet exceeded practical fetch size this "
                        "pass. See SAML10 entry below (different, newer core "
                        "family) for a same-vendor ULP current data point.",
    },
    {
        "manufacturer": "Microchip (Atmel)",
        "mcu_name": "SAML10",
        "usage_class": "ULP",
        "core": "Cortex-M23",
        "wlcsp_size_mm": None,
        "wlcsp_area_mm2": None,
        "die_size_mm2": None,
        "process_node_nm": None,
        "run_uA_per_MHz": 25,
        "sleep_current_uA": 0.1,
        "source_note": "NOT the same family as SAMD11 (different, newer "
                        "Cortex-M23-based ULP line) -- included as the best "
                        "available same-vendor active/sleep current data point "
                        "since SAMD11-specific figures weren't found. Distributor "
                        "listing: <25 uA/MHz active mode, <100 nA sleep mode, "
                        "EEMBC ULPMark score 405. Package/die data not found.",
    },
    {
        "manufacturer": "Microchip (Atmel)",
        "mcu_name": "SAM D21/DA1",
        "usage_class": "ULP",
        "core": "Cortex-M0+",
        "wlcsp_size_mm": (2.7, 2.7),
        "wlcsp_area_mm2": 7.29,
        "die_size_mm2": None,
        "process_node_nm": None,
        "run_uA_per_MHz": None,
        "sleep_current_uA": None,
        "source_note": "45-ball WLCSP, 2.7x2.7mm (JEDEC MO-220) -- dims "
                        "search-derived from a datasheet mirror, not "
                        "independently table-verified, but consistent with "
                        "Digi-Key listings. Active/standby current and process "
                        "node not found: repeated attempts against the full "
                        "DS40001882 datasheet (Microchip, Sparkfun, Adafruit, "
                        "Octopart mirrors) all failed to surface the "
                        "electrical-characteristics table text; only anecdotal "
                        "community-measured board-level numbers exist and are "
                        "deliberately not reported here as datasheet figures.",
    },
    {
        "manufacturer": "Microchip (Atmel)",
        "mcu_name": "SAM D5x/E5x",
        "usage_class": "High-performance",
        "core": "Cortex-M4F",
        "wlcsp_size_mm": None,
        "wlcsp_area_mm2": None,
        "die_size_mm2": None,
        "process_node_nm": None,
        "run_uA_per_MHz": 65,
        "sleep_current_uA": None,
        "source_note": "Package confirmed as \"64-Pin WLCSP\" option in "
                        "datasheet ToC/pinout list; exact mm dimensions not "
                        "found (DS60001507 package table didn't surface in "
                        "extraction). Active current 65 uA/MHz is Microchip's "
                        "own headline \"class-leading 65 uA/MHz active power\" "
                        "spec for SAM D51/E51 (product literature, not a raw "
                        "table pull). Standby current and process node not "
                        "found.",
    },

    # ------------------------------------------------------------------
    # Ambiq (ultra-low-power focused, Apollo family)
    # ------------------------------------------------------------------
    {
        "manufacturer": "Ambiq",
        "mcu_name": "Apollo3 Blue",
        "usage_class": "ULP",
        "core": "Cortex-M4F",
        "wlcsp_size_mm": (3.25, 3.37),
        "wlcsp_area_mm2": 10.95,
        "die_size_mm2": None,
        "process_node_nm": 40,
        "run_uA_per_MHz": 6,
        "sleep_current_uA": 1,
        "source_note": "Ambiq product page: <6 uA/MHz active power, 1 uA deep "
                        "sleep -- among the lowest active-power figures found "
                        "across all vendors here. WLCSP part AMAP31KK-KCR: "
                        "3.25x3.37mm, 66-pin (distributor product page citing "
                        "Ambiq specs). Process node IS disclosed (just not in "
                        "the datasheet itself): TSMC 40nm ULP (40ULP) combined "
                        "with Ambiq's Subthreshold Power Optimized Technology "
                        "(SPOT), confirmed via TSMC's own press release "
                        "(\"Ambiq Micro Achieves World-Leading Power "
                        "Consumption Performance with TSMC 40ULP Technology\", "
                        "pr.tsmc.com/english/news/1999).",
    },
    {
        "manufacturer": "Ambiq",
        "mcu_name": "Apollo4 Blue Plus",
        "usage_class": "ULP",
        "core": "Cortex-M4F",
        "wlcsp_size_mm": None,
        "wlcsp_area_mm2": None,
        "die_size_mm2": None,
        "process_node_nm": None,
        "run_uA_per_MHz": 4,
        "sleep_current_uA": None,
        "source_note": "NOT offered in WLCSP -- confirmed BGA-only: KBR/KXR "
                        "package, 4.7x4.7mm, 12x12 BGA, 131 pins/81 GPIO. "
                        "Included for reference/run-current comparison despite "
                        "not being WLCSP. Active current 4 uA/MHz is the "
                        "datasheet headline spec (up to 192MHz). Deep sleep "
                        "current not found (datasheet references a numeric "
                        "table on p.209 that couldn't be retrieved this pass). "
                        "Process node/foundry not disclosed (unlike Apollo3, "
                        "no confirming press release found this session; "
                        "Apollo5/Apollo510 is separately confirmed as TSMC "
                        "22nm, for contrast only -- not applicable to Apollo4). "
                        "Source: ambiq.com Apollo4 Blue Plus SoC Datasheet.",
    },

    # ------------------------------------------------------------------
    # Texas Instruments
    # ------------------------------------------------------------------
    {
        "manufacturer": "Texas Instruments",
        "mcu_name": "MSP430FR2433",
        "usage_class": "ULP",
        "core": "MSP430 (non-ARM, 16-bit)",
        "wlcsp_size_mm": (2.29, 2.34),
        "wlcsp_area_mm2": 5.36,
        "die_size_mm2": None,
        "process_node_nm": None,
        "run_uA_per_MHz": 126,
        "sleep_current_uA": 0.055,  # LPM4.5, deepest state
        "source_note": "FRAM-based ultra-low-power family, DSBGA package code "
                        "YQW. Active: 126 uA/MHz typical, VCC=3V/25C, 8MHz, "
                        "executing from FRAM with 75% cache hit ratio. Sleep "
                        "states (VCC=3V/25C): LPM3 (XT1, w/ SVS) 1.65 uA; "
                        "LPM3.5 0.95 uA; LPM4 0.35 uA; LPM4.5 (deepest, "
                        "reported here) 55 nA. Core is TI's proprietary "
                        "MSP430 16-bit RISC architecture, not ARM Cortex. "
                        "Source: MSP430FR2433 datasheet SLASE59F, ti.com/lit/"
                        "ds/symlink/msp430fr2433.pdf",
    },
    {
        "manufacturer": "Texas Instruments",
        "mcu_name": "CC2340R5",
        "usage_class": "ULP",
        "core": "Cortex-M0+",
        "wlcsp_size_mm": (2.2, 2.6),
        "wlcsp_area_mm2": 5.72,
        "die_size_mm2": None,
        "process_node_nm": None,
        "run_uA_per_MHz": 54,
        "sleep_current_uA": 0.71,  # Standby, RTC + full RAM retention
        "source_note": "SimpleLink BLE wireless MCU, YBG WCSP package "
                        "(2.2x2.6mm, 28 pins, 0.4mm pitch) -- also offered in "
                        "QFN24/QFN40, WLCSP confirmed as genuine option. Fixed "
                        "48 MHz core. Datasheet doesn't give a native uA/MHz "
                        "figure; run_uA_per_MHz here is derived: 2.6 mA typical "
                        "running CoreMark from flash (VDDS=3.0V, DCDC enabled, "
                        "25C) / 48MHz = 54.2 uA/MHz. RX(1Mbps) 5.3mA, TX(0dBm) "
                        "5.1mA are radio current, not core. Standby 0.71 uA "
                        "(RTC + full RAM retention, LFOSC, optimized DCDC); "
                        "Shutdown (no retention) 165 nA. Source: SWRS272F, "
                        "ti.com/lit/ds/symlink/cc2340r5.pdf",
    },
    {
        "manufacturer": "Texas Instruments",
        "mcu_name": "MSPM0C1104",
        "usage_class": "Low-cost",
        "core": "Cortex-M0+",
        "wlcsp_size_mm": (1.6, 0.86),
        "wlcsp_area_mm2": 1.38,
        "die_size_mm2": None,
        "process_node_nm": None,
        "run_uA_per_MHz": 87,
        "sleep_current_uA": 5.1,  # STANDBY0, timers enabled at 32kHz
        "source_note": "DSBGA-8 package \"YCJ\", 1.6x0.86mm -- one of the "
                        "smallest packaged MCUs on the market (TI markets "
                        "MSPM0C as the world's smallest/cheapest general-"
                        "purpose MCU, not ULP-branded). 24MHz max. Active: 87 "
                        "uA/MHz typical, VDD=3.3V, while(1) from flash @24MHz, "
                        "25C. STANDBY0 5.1 uA; Shutdown 200 nA. NOTE: a "
                        "\"Stop0\" figure of 609 uA also appears in the "
                        "datasheet extraction and looks anomalously high "
                        "relative to STANDBY0/Shutdown -- likely a different, "
                        "higher-power stop variant, flagged for manual "
                        "reconciliation, not used here. Source: MSPM0C110x/"
                        "MSPS003 datasheet, ti.com/lit/ds/symlink/"
                        "mspm0c1104.pdf",
    },
    {
        "manufacturer": "Texas Instruments",
        "mcu_name": "MSPM0G1507",
        "usage_class": "Low-cost",
        "core": "Cortex-M0+",
        "wlcsp_size_mm": (2.65, 1.57),
        "wlcsp_area_mm2": 4.16,
        "die_size_mm2": None,
        "process_node_nm": None,
        "run_uA_per_MHz": 101,
        "sleep_current_uA": 1.5,
        "source_note": "Higher-performance MSPM0 line with integrated analog "
                        "(2x 4Msps ADC, 12-bit DAC, opamps). DSBGA package "
                        "\"YCJ\", 2.65x1.57mm, 28 pins, up to 80MHz. Active: "
                        "101 uA/MHz typical (CoreMark). Sleep: 1.5 uA (32kHz "
                        "LFXT, RTC, SRAM/CPU state retained); Stop 190 uA "
                        "@4MHz (not a true deep-sleep figure). Process node "
                        "not publicly disclosed. Source: SLASEW9E, ti.com/lit/"
                        "ds/symlink/mspm0g1507.pdf",
    },

    # ------------------------------------------------------------------
    # NXP
    # ------------------------------------------------------------------
    {
        "manufacturer": "NXP",
        "mcu_name": "Kinetis KL02",
        "usage_class": "ULP",
        "core": "Cortex-M0+",
        "wlcsp_size_mm": (1.99, 1.94),
        "wlcsp_area_mm2": 3.86,
        "die_size_mm2": None,
        "process_node_nm": 90,
        "run_uA_per_MHz": 79,
        "sleep_current_uA": 3.3,  # VLPS, midpoint of 2.3-4.28uA range
        "source_note": "20-pin WLCSP \"AF\", 1.99x1.94x0.56mm, 0.4mm pitch. "
                        "Process: 90nm NXP Thin Film Storage (TFS) low-leakage "
                        "technology. Active: 3.6-4mA @48MHz core/24MHz flash, "
                        "bus clock disabled, while(1) from flash, 3.0V -> "
                        "~75-83 uA/MHz (79 midpoint reported). VLPS "
                        "(very-low-power stop): 2.3-4.28 uA typ/max @3.0V/25C "
                        "(3.3 midpoint reported). Source: KL02P20M48SF0.pdf "
                        "Rev.5, NXP fact sheet KINETISKL02CSPFS.pdf",
    },
    {
        "manufacturer": "NXP",
        "mcu_name": "Kinetis KL03",
        "usage_class": "ULP",
        "core": "Cortex-M0+",
        "wlcsp_size_mm": (2.0, 1.61),
        "wlcsp_area_mm2": 3.22,
        "die_size_mm2": None,
        "process_node_nm": 90,
        "run_uA_per_MHz": 121,
        "sleep_current_uA": 3.3,  # not independently measured, KL02 proxy
        "source_note": "20-pin WLCSP \"AF\", 2.0x1.61x0.56mm (also an "
                        "ultra-thin \"BF\" variant at 0.32mm height). Same "
                        "90nm TFS process family as KL02. Active: 5.71-5.94mA "
                        "@48MHz core/24MHz flash, bus clock disabled, 3.0V -> "
                        "~119-124 uA/MHz (121 midpoint). FLAGGED: this is "
                        "markedly higher per-MHz than KL02 under nominally "
                        "identical conditions -- worth a manual check against "
                        "the primary Table 11 row before use, may reflect a "
                        "different measurement row. VLPS not distinctly "
                        "re-extracted this pass; KL02's 3.3 uA figure used as "
                        "a same-family proxy. Source: KL03P24M48SF0.pdf "
                        "Rev.5.1",
    },
    {
        "manufacturer": "NXP",
        "mcu_name": "LPC802",
        "usage_class": "Low-cost",
        "core": "Cortex-M0+",
        "wlcsp_size_mm": (1.84, 1.84),
        "wlcsp_area_mm2": 3.39,
        "die_size_mm2": None,
        "process_node_nm": None,
        "run_uA_per_MHz": 85,
        "sleep_current_uA": 0.15,  # Deep power-down, typical
        "source_note": "Entry-level LPC80x line, positioned by NXP as a "
                        "\"low-cost 32-bit MCU family\" (8-bit-alternative "
                        "framing). WLCSP16, 1.84x1.84x0.5mm (also TSSOP16/20, "
                        "HVQFN33 5x5x0.85mm). Up to 15MHz. Active ~1.0mA typ "
                        "@12MHz -> ~83 uA/MHz, 1.3mA @15MHz -> ~87 uA/MHz "
                        "(85 midpoint reported), 3.3V, GPIO low, peripherals "
                        "disabled. Deep power-down 0.15 uA typ/0.5 uA max "
                        "(3.3V/25C, WAKEUP pin high); Power-down 6 uA typ/14 "
                        "uA max. Process node not found. Source: LPC802.pdf, "
                        "nxp.com/docs/en/data-sheet/LPC802.pdf",
    },
    {
        "manufacturer": "NXP",
        "mcu_name": "LPC804",
        "usage_class": "Low-cost",
        "core": "Cortex-M0+",
        "wlcsp_size_mm": (2.50, 1.84),
        "wlcsp_area_mm2": 4.60,
        "die_size_mm2": None,
        "process_node_nm": None,
        "run_uA_per_MHz": None,
        "sleep_current_uA": None,
        "source_note": "Same LPC80x entry-level family as LPC802. WLCSP20, "
                        "2.50x1.84x0.5mm (5x4 bump array, also TSSOP20/24, "
                        "HVQFN33). Run/sleep current not independently pulled "
                        "this pass; expect a similar order to LPC802 "
                        "(~80-90 uA/MHz active) given shared core/process. "
                        "Source: LPC804_DS.pdf, nxp.com/docs/en/nxp/"
                        "data-sheets/LPC804_DS.pdf",
    },

    # ------------------------------------------------------------------
    # Silicon Labs
    # ------------------------------------------------------------------
    {
        "manufacturer": "Silicon Labs",
        "mcu_name": "EFM32HG (Happy Gecko)",
        "usage_class": "ULP",
        "core": "Cortex-M0+",
        "wlcsp_size_mm": (3.0, 3.0),
        "wlcsp_area_mm2": 9.00,
        "die_size_mm2": None,
        "process_node_nm": None,
        "run_uA_per_MHz": 127,
        "sleep_current_uA": 0.9,  # EM2, RTC + 32.768kHz osc, RAM/CPU retained
        "source_note": "USB-enabled ULP line (\"lowest USB power consumption "
                        "in the industry\" per Silabs). CSP36, 3x3mm, 36 balls "
                        "(also QFN24/32, TQFP48). 25MHz max. Active (EM0): 127 "
                        "uA/MHz, 24MHz HFRCO, peripheral clocks off, VDD=3.0V, "
                        "25C. Sleep: EM2 0.9 uA (reported), EM3 0.6 uA, EM4 20 "
                        "nA (deepest) -- all @3V/25C. Process node not found. "
                        "Source: efm32hg-datasheet.pdf Rev 2.42, silabs.com",
    },
    {
        "manufacturer": "Silicon Labs",
        "mcu_name": "EFR32BG1 (Blue Gecko, Series 1)",
        "usage_class": "ULP",
        "core": "Cortex-M4",
        "wlcsp_size_mm": (3.3, 3.14),
        "wlcsp_area_mm2": 10.36,
        "die_size_mm2": None,
        "process_node_nm": None,
        "run_uA_per_MHz": 63,
        "sleep_current_uA": 0.58,  # EM4H Hibernate, 128B RAM retention
        "source_note": "BLE SoC, \"energy-friendly\" framing. 43-pin "
                        "CSP/WLCSP43, 3.3x3.14mm. 40MHz max. Active (EM0): 63 "
                        "uA/MHz, 38MHz HFRCO, CPU from flash, DC-DC low-noise "
                        "DCM mode. Sleep: EM4H Hibernate 0.58 uA (128B RAM "
                        "retention, DC-DC enabled) -- lowest documented state, "
                        "reported here. Process node not found. Source: "
                        "efr32bg1-csp-datasheet.pdf Rev 1.3, silabs.com",
    },
    {
        "manufacturer": "Silicon Labs",
        "mcu_name": "EFR32BG24 (Blue Gecko, Series 2)",
        "usage_class": "High-performance",
        "core": "Cortex-M33",
        "wlcsp_size_mm": (3.1, 3.0),
        "wlcsp_area_mm2": 9.30,
        "die_size_mm2": None,
        "process_node_nm": 40,
        "run_uA_per_MHz": 33.4,
        "sleep_current_uA": 1.3,  # EM2, 16kB RAM retention
        "source_note": "BLE/Matter/Thread-class SoC with DSP+FPU and security "
                        "core, higher-end than BG1. WLCSP42, 3.1x3.0x0.4mm. "
                        "78MHz max. Active (EM0): 33.4 uA/MHz w/ DC-DC "
                        "(VSCALE1) or 47.1 uA/MHz direct supply, both at "
                        "39MHz crystal/while-loop-from-flash, 3.0V (lower "
                        "DC-DC figure reported). Sleep: EM2 1.3 uA (16kB RAM "
                        "retention, LFRCO RTC, DC-DC, 3.0V) reported; EM3 1.1 "
                        "uA, EM4 0.25 uA (deepest, no BURTC/LF osc). Process "
                        "node 40nm confirmed (Silicon Labs Series 2 "
                        "platform-wide, multiple device pages). Source: "
                        "efr32bg24-datasheet-CSP.pdf Rev 1.0, silabs.com",
    },
    {
        "manufacturer": "Silicon Labs",
        "mcu_name": "EFM32WG (Wonder Gecko)",
        "usage_class": "High-performance",
        "core": "Cortex-M4F",
        "wlcsp_size_mm": None,
        "wlcsp_area_mm2": None,
        "die_size_mm2": None,
        "process_node_nm": None,
        "run_uA_per_MHz": 211,
        "sleep_current_uA": 0.95,  # EM2
        "source_note": "General-purpose high-end Gecko line. CSP81 (81-ball "
                        "chip-scale) confirmed offered but exact mm dims not "
                        "found (datasheet package section didn't surface in "
                        "extraction, two attempts) -- also QFN64, TQFP64, "
                        "LQFP100, BGA112/120. 48MHz max. Active (EM0): 211 "
                        "uA/MHz, 48MHz HFXO, peripheral clocks off, VDD=3.0V, "
                        "25C. Sleep: EM2 0.95 uA (reported), EM3 0.65 uA, EM4 "
                        "20nA (or 0.4uA with RTC). Process node not found. "
                        "Same CSP81 package family also offered on EFM32LG "
                        "(Leopard Gecko), not independently pulled. Source: "
                        "efm32wg-datasheet.pdf Rev 2.44, silabs.com",
    },

    # ------------------------------------------------------------------
    # onsemi
    # ------------------------------------------------------------------
    {
        "manufacturer": "onsemi",
        "mcu_name": "RSL10",
        "usage_class": "ULP",
        "core": "Cortex-M3 (+ LPDSP32 DSP)",
        "wlcsp_size_mm": (2.325, 2.364),
        "wlcsp_area_mm2": 5.50,
        "die_size_mm2": None,
        "process_node_nm": None,
        "run_uA_per_MHz": None,
        "sleep_current_uA": 0.1,  # Deep Sleep + 8kB RAM retention, 3V
        "source_note": "Bluetooth 5 Radio SoC, dual-core (Cortex-M3 + "
                        "LPDSP32 DSP), widely cited EEMBC ULPMark reference "
                        "part. WLCSP51 (part NCH-RSL10-101WC51-ABG), CASE "
                        "567MT, 2.325x2.364mm -- matches onsemi's own \"5.50 "
                        "mm2 WLCSP\" marketing figure; also offered in QFN48 "
                        "6x6mm. No native uA/MHz table in the datasheet -- "
                        "instead reported as CoreMark efficiency: 108 "
                        "CoreMark/mA at VBAT=1.25V, 257 CoreMark/mA at "
                        "VBAT=3V (Cortex-M3+LPDSP32 running CoreMark from RAM, "
                        "48MHz SYSCLK). run_uA_per_MHz left None -- not "
                        "directly convertible without a CoreMark/MHz "
                        "assumption. Sleep states (VBAT=1.25V/3V): Deep Sleep "
                        "IO-wakeup-only 50/25 nA; Deep Sleep + 32kHz osc + "
                        "interrupt 90/40 nA; Deep Sleep + 8kB RAM retention "
                        "300/100 nA (100nA reported here); Standby Mode "
                        "(digital blocks unclocked) 30/17 uA -- a distinct, "
                        "shallower state. Source: onsemi RSL10 Datasheet "
                        "Rev.3, onsemi.com/pdf/datasheet/ncv-rsl10-d.pdf",
    },

    # ------------------------------------------------------------------
    # Renesas (including the former Dialog Semiconductor BLE line)
    # ------------------------------------------------------------------
    {
        "manufacturer": "Renesas (ex-Dialog Semiconductor)",
        "mcu_name": "DA14531 SmartBond TINY",
        "usage_class": "ULP",
        "core": "Cortex-M0+",
        "wlcsp_size_mm": (1.7, 2.05),
        "wlcsp_area_mm2": 3.49,
        "die_size_mm2": None,
        "process_node_nm": None,
        "run_uA_per_MHz": 23.75,
        "sleep_current_uA": 0.27,  # Hibernation, 0kB RAM retained, VBAT_HIGH
        "source_note": "BLE 5.1 SoC marketed for disposables/beacons/trackers, "
                        "coin-cell targeted. WLCSP17, 1.7x2.05mm, 0.5mm pitch "
                        "(also FCGQFN24 2.2x3mm). 16MHz Cortex-M0+. Active: "
                        "VBAT_LOW (boost, 1.5V) mode 830 uA typ -> 51.9 "
                        "uA/MHz; VBAT_HIGH (buck, 3.0V, DCDC on) mode 380 uA "
                        "typ -> 23.75 uA/MHz (lower figure, VBAT_HIGH, "
                        "reported here) -- both CPU from RAM on XTAL32M "
                        "@16MHz. Sleep: Hibernation 0kB RAM retained, "
                        "VBAT_HIGH=3V: 270 nA (reported here); with 48kB RAM "
                        "retained 750 nA; Extended-sleep (48kB RAM, RCX clock) "
                        "1.6 uA; Deep-sleep (0kB RAM) 1 uA. Acquired by "
                        "Renesas from Dialog Semiconductor in 2021. Source: "
                        "Renesas DA14531 Datasheet R18DS0050EE0380 Rev.3.8, "
                        "renesas.com/en/document/dst/da14531-datasheet",
    },
    {
        "manufacturer": "Renesas",
        "mcu_name": "RA4L1",
        "usage_class": "ULP",
        "core": "Cortex-M33",
        "wlcsp_size_mm": (3.64, 4.28),
        "wlcsp_area_mm2": 15.58,
        "die_size_mm2": None,
        "process_node_nm": None,
        "run_uA_per_MHz": 168,
        "sleep_current_uA": 1.70,  # Software Standby, all SRAM retained
        "source_note": "TrustZone-enabled, positioned by Renesas as "
                        "\"ultra-low-power\". WLCSP72 (package code "
                        "SUBG0072LB-A), 3.64x4.28mm, 0.4mm pitch. Up to 80MHz. "
                        "Active: High-speed mode 80MHz, all peripheral clocks "
                        "disabled, cache disabled, executing from flash: 13.4 "
                        "mA typ -> 168 uA/MHz (reported); all peripheral "
                        "clocks enabled: 30.7 mA typ -> 384 uA/MHz. VCC=3.3V, "
                        "HOCO clock source. Software Standby, all SRAM "
                        "retained, 25C: 1.70 uA typ (max 117 uA at 125C); "
                        "16KB-SRAM-only retained variant 1.65 uA typ. Process "
                        "node not disclosed (a Renesas 22nm MCU press release "
                        "exists but does not name RA4L1). Source: Renesas "
                        "RA4L1 Group Datasheet R01DS0447EJ0131 Rev.1.31, "
                        "renesas.com/en/document/dst/ra4l1-group-datasheet",
    },
    {
        "manufacturer": "Renesas",
        "mcu_name": "RA2E1",
        "usage_class": "Low-cost",
        "core": "Cortex-M23",
        "wlcsp_size_mm": (2.14, 2.27),
        "wlcsp_area_mm2": 4.86,
        "die_size_mm2": None,
        "process_node_nm": None,
        "run_uA_per_MHz": 100,
        "sleep_current_uA": 0.25,  # Software Standby, all SRAM on
        "source_note": "Entry-level, cost-sensitive line, marketed \"ultra "
                        "low power\" but positioned as general-purpose "
                        "entry-level rather than a dedicated ULP part -- "
                        "classed Low-cost here. WLCSP 25-pin, 2.14x2.27mm, "
                        "0.4mm pitch. Up to 48MHz. Active: High-speed mode, "
                        "normal mode, all peripheral clocks disabled, "
                        "CoreMark from flash, VCC=3.3V: 4.80 mA typ @48MHz -> "
                        "100 uA/MHz (reported); 1.40 mA typ @8MHz -> 175 "
                        "uA/MHz; all peripheral clocks enabled @48MHz: 13.0 mA "
                        "max -> 270.8 uA/MHz. Software Standby, all SRAM on, "
                        "25C: 0.25 uA typ/1.3 uA max. Process node not found. "
                        "Source: Renesas RA2E1 Group Datasheet "
                        "R01DS0386EJ0170 Rev.1.70, renesas.com/en/document/"
                        "dst/ra2e1-group-datasheet",
    },

    # ------------------------------------------------------------------
    # Infineon / Cypress
    # ------------------------------------------------------------------
    {
        "manufacturer": "Infineon (ex-Cypress)",
        "mcu_name": "PSoC 4000S",
        "usage_class": "Low-cost",
        "core": "Cortex-M0+",
        "wlcsp_size_mm": (2.02, 1.93),
        "wlcsp_area_mm2": 3.90,
        "die_size_mm2": None,
        "process_node_nm": None,
        "run_uA_per_MHz": 95.8,
        "sleep_current_uA": 2.5,  # Deep Sleep, I2C wakeup + WDT on
        "source_note": "Marketed as a capacitive-sensing/general-purpose "
                        "value line. 25-ball WLCSP, 2.02x1.93x0.48mm, 0.35mm "
                        "pitch. Up to 48MHz. Active, VDD=3.3V/25C, executing "
                        "from flash: 1.2 mA typ @6MHz -> 200 uA/MHz; 2.4 mA "
                        "typ @24MHz -> 100 uA/MHz; 4.6 mA typ (max 5.9mA) "
                        "@48MHz -> 95.8 uA/MHz (48MHz figure reported, best "
                        "efficiency point). Deep Sleep (I2C wakeup + WDT on), "
                        "VDD=1.8-3.6V: 2.5 uA typ/60 uA max. A separate "
                        "\"Sleep\" mode with I2C/WDT/comparators on draws "
                        "0.7-1.9 mA -- not a true deep-sleep state, not used "
                        "here. Process node not found. Source: Infineon PSoC "
                        "4000S MCU Datasheet 002-00123 Rev *Q, infineon.com",
    },
    {
        "manufacturer": "Infineon (ex-Cypress)",
        "mcu_name": "PSoC 6 (CY8C61x6/CY8C61x7)",
        "usage_class": "High-performance",
        "core": "Cortex-M4F + Cortex-M0+",
        "wlcsp_size_mm": (3.676, 3.190),
        "wlcsp_area_mm2": 11.73,
        "die_size_mm2": None,
        "process_node_nm": None,
        "run_uA_per_MHz": 40,
        "sleep_current_uA": 7,  # Deep Sleep, 64KB SRAM retention
        "source_note": "Dual-core secure MCU platform, marketed \"high-"
                        "performance, ultra-low-power\" (hybrid framing, "
                        "classed High-performance here for the M4F app core). "
                        "In this PSoC61 sub-line the CM0+ is reserved for "
                        "system use; the sibling PSoC62 line (CY8C62x6/x7) "
                        "exposes both cores to applications and reportedly "
                        "also offers an 80-WLCSP, but its datasheet couldn't "
                        "be fetched this pass -- flagged unverified, not "
                        "included as a separate row. 80-ball WLCSP, "
                        "3.676x3.190mm, 0.43mm height (also a \"Thin\" variant "
                        "at 0.33mm), 0.35mm pitch. Up to 150MHz (M4F) / "
                        "100MHz (M0+). Active current given as a vendor "
                        "voltage-scaling slope rather than one datasheet "
                        "figure: at 1.1V core logic, CM4 40 uA/MHz (reported), "
                        "CM0+ 20 uA/MHz; at 0.9V core logic (ULP mode), CM4 22 "
                        "uA/MHz, CM0+ 15 uA/MHz. Example measured point: CM4 "
                        "active 50MHz + CM0+ sleep 25MHz, execute from flash, "
                        "IMO&FLL, VDDD=3.3V, Buck ON, max 60C: 2.3 mA typ/3.2 "
                        "mA max. Deep Sleep: 7 uA typ (64KB SRAM retention, "
                        "reported here), 9 uA typ (256KB SRAM retention); "
                        "Hibernate (no clocks): 300 nA (VDDD=1.8V)/800 nA "
                        "(VDDD=3.3V). Process node not found (unsourced web "
                        "mentions of 40nm exist but not confirmed to an "
                        "Infineon/Cypress document). Source: Cypress/Infineon "
                        "PSoC 6 MCU CY8C61x6/CY8C61x7 Datasheet 002-21414 "
                        "Rev *K.",
    },
]


def to_dataframe():
    """Optional convenience: return as a pandas DataFrame if pandas is
    available. Falls back gracefully if it isn't."""
    try:
        import pandas as pd
    except ImportError:
        raise ImportError("pandas not installed; use MCU_DATA (list of dicts) directly instead.")
    df = pd.DataFrame(MCU_DATA)
    return df


def print_summary_table():
    """Print a compact, aligned text table without needing pandas."""
    headers = ["Manufacturer", "MCU", "Class", "Core", "WLCSP(mm)",
               "Node(nm)", "Run(uA/MHz)", "Sleep(uA)"]
    rows = []
    for d in MCU_DATA:
        wlcsp = f"{d['wlcsp_size_mm'][0]}x{d['wlcsp_size_mm'][1]}" if d["wlcsp_size_mm"] else "N/A"
        node = str(d["process_node_nm"]) if d["process_node_nm"] is not None else "N/A"
        run = str(d["run_uA_per_MHz"]) if d["run_uA_per_MHz"] is not None else "N/A"
        sleep = str(d["sleep_current_uA"]) if d["sleep_current_uA"] is not None else "N/A"
        rows.append([d["manufacturer"], d["mcu_name"], d["usage_class"],
                     d["core"], wlcsp, node, run, sleep])

    widths = [max(len(str(r[i])) for r in ([headers] + rows)) for i in range(len(headers))]
    fmt = "  ".join(f"{{:<{w}}}" for w in widths)
    print(fmt.format(*headers))
    print(fmt.format(*["-" * w for w in widths]))
    for r in rows:
        print(fmt.format(*r))


if __name__ == "__main__":
    print_summary_table()
    print("\nNote: die_size_mm2 is None for every entry -- no vendor-disclosed "
          "die size was found for any of these parts, even after a further "
          "search attempt (teardown/die-photo reports are paywalled). Use "
          "wlcsp_area_mm2 as the best available proxy where present.")
    print("\nNote on run/sleep current comparability: figures come from "
          "different measurement conditions per vendor/part (regulator mode, "
          "cache state, voltage, what 'sleep' means). Re-check the specific "
          "datasheet before using in a publication -- see source_note per entry.")
