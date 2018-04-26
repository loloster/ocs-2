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
// -------------------------------------------------------------------------

uint32_t LFO3_phase_old;

//----------------------------------------------------------------------------------
// LFO1
//----------------------------------------------------------------------------------

inline void init_LFO1() {
  LFO1_phase = 0x80000000;
}

inline void LFO1_freq() {
  uint32_t freq;

  freq = adc_value16[LFO1_FQ];
  freq *= freq;
  freq >>= 10;
  freq <<= LFO1_range;
  freq += LFO1_offset;
  //LFO1_increment = freq;
  LFO1_increment = (MIDI_LFO1_speed != 0)? MIDI_LFO1_speed: freq;
}

inline void LFO1_modulation() {
  uint32_t tmp, phase, symetrie, distortion, gain, offset_gain, offset, tmp2;
  int32_t offset_signed, tmpS, tmpS2;

  phase = LFO1_phase; // 32 bits
  symetrie = ((0xFFFF)-(adc_value16[LFO1_SYM]))<<16; // 32 bits
  symetrie = (0xFF000000 > symetrie)? symetrie: 0xFF000000 ; 
  symetrie = (symetrie > 0x00F00000)? symetrie: 0x00F00000 ;
  
  tmp = adc_value16[LFO1_WF];
  distortion = ( tmp & 0x8000)? 0x7FFF : tmp; // only half of the fader

  gain = tmp;
  gain = tmp - distortion; // 2nd half of the fader
  offset_gain = gain; // 15 bits
  gain *= gain; // 30 bits max
  gain >>= 15;
  gain *= offset_gain;
  //gain >>= 15; // 15 bits

  offset_signed = 0x7FFF - (symetrie>>16); // from -1 to 1; 15 bit + sign
  offset_signed *= offset_gain; // 15 + 15 + sign
  offset_signed >>= 15; 
  
  // calcul de la symetrie
  tmp = (phase > (symetrie))? -phase / (-symetrie >> 16): phase / (symetrie >> 16); 
  // gain pour passage sin -> square
  tmpS = tmp - (1<<15) + offset_signed; // passage en signed
  tmpS *= (1 << 11) + (gain >> 15);
  tmpS >>= 11;
  tmpS = (tmpS < -0x7FFF)? -0x7FFF: tmpS; // clip low
  tmpS = (tmpS >  0x7F00)?  0x7F00: tmpS; // clip high
  
  // calcul du sinus
  tmpS2 = (2*tmpS) - ((tmpS*abs(tmpS)) >> 15);
  //mix tri -> sinus
  tmpS = MIX16U(tmpS, tmpS2, distortion*2); // 15 bit + sign
  
  modulation_data[mod_LFO1] = tmpS;  
  #ifdef LFO_out
    analog_out_1((modulation_data[mod_LFO1]+(1<<15))<<16);
  #endif
}

inline void LFO1() {
  LFO1_phase += LFO1_increment;
}

//----------------------------------------------------------------------------------
// LFO2
//----------------------------------------------------------------------------------

inline void init_LFO2() {
  LFO2_phase = 0x80000000;
}

inline void LFO2_freq() {
  uint32_t freq;

  freq = adc_value16[LFO2_FQ];
  freq *= freq;
  freq >>= 10;
  freq += 1000;
  freq <<= LFO2_range;
  freq += LFO2_offset;
  LFO2_increment = freq;
  
  LFO2_increment = (MIDI_LFO2_speed != 0)? MIDI_LFO2_speed: LFO2_increment;
}

inline void LFO2_modulation() {
  uint32_t tmp, phase, symetrie, distortion, gain, offset_gain, offset, tmp2;
  int32_t offset_signed, tmpS, tmpS2;

  phase = LFO2_phase; // 32 bits
  symetrie = ((0xFFFF)-(adc_value16[LFO2_SYM]))<<16; // 32 bits
  symetrie = (0xFF000000 > symetrie)? symetrie: 0xFF000000 ; 
  symetrie = (symetrie > 0x00F00000)? symetrie: 0x00F00000 ;
  
  tmp = adc_value16[LFO2_WF];
  distortion = ( tmp & 0x8000)? 0x7FFF : tmp; // only half of the fader

  gain = tmp;
  gain = tmp - distortion; // 2nd half of the fader
  offset_gain = gain; // 15 bits
  gain *= gain; // 30 bits max
  gain >>= 15;
  gain *= offset_gain;
  //gain >>= 15; // 15 bits

  offset_signed = 0x7FFF - (symetrie>>16); // from -1 to 1; 15 bit + sign
  offset_signed *= offset_gain; // 15 + 15 + sign
  offset_signed >>= 15; 
  
  // calcul de la symetrie
  tmp = (phase > (symetrie))? -phase / (-symetrie >> 16): phase / (symetrie >> 16); 
  // gain pour passage sin -> square
  tmpS = tmp - (1<<15) + offset_signed; // passage en signed
  tmpS *= (1 << 11) + (gain >> 15);
  tmpS >>= 11;
  tmpS = (tmpS < -0x7FFF)? -0x7FFF: tmpS; // clip low
  tmpS = (tmpS >  0x7F00)?  0x7F00: tmpS; // clip high
  
  // calcul du sinus
  tmpS2 = (2*tmpS) - ((tmpS*abs(tmpS)) >> 15);
  //mix tri -> sinus
  tmpS = MIX16U(tmpS, tmpS2, distortion*2); // 15 bit + sign
  
  modulation_data[mod_LFO2] = tmpS;  
  #ifdef LFO_out
    analog_out_2((modulation_data[mod_LFO2]+(1<<15))<<16);
  #endif
}

inline void LFO2() {
  LFO2_phase += LFO2_increment;
}

//----------------------------------------------------------------------------------
// LFO3
//----------------------------------------------------------------------------------

inline void init_LFO3() {
  LFO3_phase = 0x80000000;
  MIDI_LFO_FQ = 0;
}

inline void LFO3_freq() { 
  uint32_t freq;
  int32_t tmp;
  
  #ifdef LFO3_NO_MIDI
    if (true)
  #endif
  #ifndef LFO3_NO_MIDI
    if (MIDI_LFO_FQ == 0) 
  #endif
  {
    freq = adc_value16[LFO3_FQ];
    tmp = adc_value[LFO3_MOD] * modulation_data[modulation_index[index_LFO3_MOD]];
    freq += tmp>>14;
    freq += 1<<20;
    freq = (freq < 0x000FFFFF)? 0x00000000 : freq-0x000FFFFF;
    freq = (freq > 0x0000FFFF)? 0x0000FFFF : freq;
  
    freq *= freq;
    freq >>= 10;
    freq += 1500;
    LFO3_increment = freq;
    
    LFO3_increment = (MIDI_LFO3_speed != 0)? MIDI_LFO3_speed: LFO3_increment;
    LFO3_phase_distord = 0;
  }
  else {
    //LFO3_increment = MIDI_LFO_FQ;
    tmp = MIDI_LFO_FQ;
    freq = adc_value16[LFO3_FQ] >> 13;
    tmp <<= freq;
    tmp >>= 4;
    LFO3_increment = tmp;
    LFO3_phase_distord = adc_value16[LFO3_MOD];
  }
  
  #ifndef LFO3_NO_MIDI
    tmp = LFO3_MIDI_count;
    if (tmp > (1<<18)) { //about 6 sec
      MIDI_LFO_FQ = 0; // do not use MIDI timming
      tmp = (1<<18); // limit LFO3_MIDI_count to avoid roll back to 0
    }
  #endif
}

inline void LFO3_modulation() {
  uint32_t tmp, tmp2;
  uint32_t phaseL, phaseH;
  uint32_t real_phase;

  tmp = LFO3_phase >> 16;
  tmp = (tmp*tmp) >> 16;
  tmp2 = LFO3_phase - tmp*tmp;
  real_phase = LFO3_phase - (tmp2>>16) * LFO3_phase_distord;

  switch (LFO3_WF) { 
  case 0: // sinus
    tmp=table_cos[real_phase >> 19];
    tmp = (tmp >> 16) - (1<<15);     
    break;
  case 1: // tri
    tmp = real_phase >> 15;
    tmp = (tmp >= 0x10000)? 0x20000 - tmp: tmp;
    tmp -= (1<<15); 
    break;
  case 2: // saw up
    tmp = real_phase >> 16 ; // keep only 16bit
    tmp -= (1<<15); // To make it symetrical
    break;
  case 3: // saw down
    tmp = real_phase >> 16 ; // keep only 16bit
    tmp = (1<<15)-tmp; 
    break;
  case 4: // square
    tmp = (real_phase > 0x80000000)? (1<<15)-1: -(1<<15)+1;
    break;
  case 5: // impulse1
    tmp = (real_phase > 0xE0000000)? (1<<15)-1: -(1<<15)+1;
    break;
  case 6: // 1 1 0 0 
    tmp = (((real_phase >>29) & 0b101) == 0b101)? (1<<15)-1: -(1<<15)+1;
    break;
  case 7: // 1 1 1 0
    tmp =  ((((real_phase >>29) & 0b101) == 0b101) || (((real_phase >>29) & 0b111 )== 0b011))? (1<<15)-1: -(1<<15)+1;
    break;
  case 8: // 1 1 0 1 0 0
    tmp = ((real_phase < 0x15555555) || ((real_phase > 0x2AAAAAAA) && (real_phase < 0x3FFFFFFF)) || ((real_phase > 0x7FFFFFFF) && (real_phase < 0x95555555)) )? (1<<15)-1: -(1<<15)+1;
    break;
  case 9: // 1 1 1 1 0
    tmp = ((real_phase < 0x19999999) || ((real_phase > 0x33333333) && (real_phase < 0x4CCCCCCC)) || ((real_phase > 0x66666666) && (real_phase < 0x7FFFFFFF)) || ((real_phase > 0x99999999) && (real_phase < 0xB3333333)) )? (1<<15)-1: -(1<<15)+1;
    break;
  case 10: // 1 1 0
    tmp = ( ((real_phase * 3) & 0x80000000) & real_phase & 0x80000000)? (1<<15)-1: -(1<<15)+1;
    break;
  case 11: // 1 1 0 0 1 0 0 0
    tmp = ((((real_phase >>28) & 0b1101) == 0b1101) || (((real_phase >>28) & 0b0111 ) == 0b0111))? (1<<15)-1: -(1<<15)+1;
    break;
  case 12: // random
    tmp = ((LFO3_phase<<3) < LFO3_phase_old)? (random32() >> 16) - (1<<15): modulation_data[mod_LFO3]; 
    LFO3_phase_old = (LFO3_phase<<3);
    break;    
  }
  modulation_data[mod_LFO3] = tmp;
  //analog_out_2(tmp<<16);
}

inline void LFO3() {
  uint32_t tmp;
  LFO3_phase += LFO3_increment;

  #ifndef LFO3_NO_MIDI
    LFO3_MIDI_count++;
  #endif
}
