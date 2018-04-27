// --------------------------------------------------------------------------
// This file is part of the OCS-2 firmware.
//
//    OCS-2 firmware is free software: you can redistribute it and/or modify
//    it under the terms of the GNU General Public License as published by
//    the Free Software Foundation, either version 3 of the License, or
//    (at your option) any later version.
//
//    OCS-2 firmware is distributed in the hope that it will be useful,
//    but WITHOUT ANY WARRANTY; without even the implied warranty of
//    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//    GNU General Public License for more details.
//
//    You should have received a copy of the GNU General Public License
//    along with OCS-2 firmware.  If not, see <http://www.gnu.org/licenses/>.
// --------------------------------------------------------------------------

// DATA format :
// audio data : uint32_t : (32 significant bit)
//
// modulation coef : int32_t
// 0 for no mudulation
// 0x0000FFFF for highest modulation (16 significant bits + sign)
// 0x8000FFFF for lowest modulation
//
// pitch : uint32_t
// 0 for lowest frequency
// 0x0FFFFFFF for highest freq (28 significat bits)
// half note every 0xO0100000
// 256 half tone (twice midi range)
// midi note range : -126 to 130;
//       from 0.005Hz to about 15KHz
//       69 is 440Hz


union uint64 {
  uint64_t U64;
  uint32_t U32[2];
};

enum adc_pos {
  VCO1_FQ,          //0x00
  VCO1_MOD1,        //0x01
  VCO1_MOD2,        //0x02
  PORTAMENTO_VALUE, //0x03
  VCO2_FQ,          //0x04
  VCO2_MOD1,        //0x05
  VCO2_MOD2,        //0x06
  VCF_FQ,           //0x07
  VCF_Q,            //0x08
  VCF_MOD1,         //0x09
  VCF_MOD2,         //0x0A
  LFO1_FQ,          //0x0B
  LFO1_WF,          //0x0C
  LFO1_SYM,         //0x0D
  ADSR_A,           //0x0E
  LFO2_FQ,          //0x0F
  LFO2_WF,          //0x10
  LFO2_SYM,         //0x11
  ADSR_D,           //0x12
  LFO3_FQ,          //0x13
  LFO3_MOD,         //0x14
  EFFECT1,          //0x15
  ADSR_S,           //0x16
  CVG1,             //0x17
  CVG2,             //0x18
  EFFECT2,          //0x19
  ADSR_R,           //0x1A
  VCA_MIX,          //0x1B
  VCA_MOD,          //0x1C
  VCA_GAIN,         //0x1D
  LDR,              //0x1E
  EXT_1,            //0x1F
  EXT_2,            //0x20
  EXT_3             //0x21
};

enum modulation_value {
  mod_VCO1,       //0xA0
  mod_VCO2,       //0xA1
  mod_LFO1,       //0xA2
  mod_LFO2,       //0xA3
  mod_LFO3,       //0xA4
  mod_CVG,        //0xA5
  mod_ADSR,       //0xA6
  mod_LDR, // light   //0xA7
  mod_ENV, // audio in envelope //0xA8
  mod_VEL, // midi velocity  //0xA9
  mod_EXT1,       //0xAA
  mod_EXT2,       //0xAB
  mod_EXT3        //0xAC
};

enum modulation_adresse {
  index_VCO1_MOD1,
  index_VCO1_MOD2,
  index_VCO2_MOD1,
  index_VCO2_MOD2,
  index_VCA_MOD,
  index_VCF_MOD1,
  index_VCF_MOD2,
  index_EFFECT_MOD,
  index_LFO3_MOD
};

const uint32_t midi_pos[] = { 
  0,
  34,
  1,
  2,
  3,
  4,
  35,
  5,
  6,
  7,
  8,
  9,
  10,
  11,
  12,
  13,
  14,
  15,
  16,
  17,
  18,
  19,
  20,
  21,
  22,
  23,
  24,
  25,
  26,
  27,
  28,
  29
};

