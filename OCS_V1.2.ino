// OCS-2
// based on arduino duo
//
// main file
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

#include <Arduino.h>
#include "ARS.h"
#include "conf.h"

#pragma GCC optimize ("-O3")


// global variables
int32_t audio_out, audio_out2, audio_inL, audio_inR2, audio_inR;

// in_ADC
uint32_t adc_value[34], adc_value16[34], adc_value_accum[34];

// in keyboard
uint32_t KEY_LOCAL_goal, NOTE_ON;
uint32_t KEY_LOCAL, KEY_global;

// in MIDI
uint32_t MIDI_gate, MIDI_pitch, MIDI_fader[36];

// portamento
uint32_t portamento;

// in_WF
uint32_t VCO1_WF, VCO2_WF;

// module VCO1
uint32_t VCO1_increment;

// module VCO2
uint32_t VCO2_increment;

// module VCF
int32_t  filter_type;
int32_t G1, G2, G3, G5;

// module VCA

// module LFO
uint32_t LFO3_WF;
uint32_t LFO1_phase, LFO1_increment;
uint32_t LFO2_phase, LFO2_increment;
uint32_t LFO3_phase, LFO3_increment;
uint32_t LFO3_MIDI_count, LFO3_phase_distord;

// module cvg
//   Random
uint32_t LFO4_phase, LFO4_increment;
uint32_t random_goal, random_filter1, random_filter2;
//   AR
uint32_t AR_value;
//   LFO4
uint32_t LFO5_phase; 
//   NL
uint32_t LFO6_phase, LFO7_phase; 

// module_ADSR
uint32_t ADSR_out;

// module EFFECT 
uint32_t EFFECT_type;

// modulation
int32_t modulation_data[13];
uint32_t modulation_index[9];

// leds 
uint32_t led1_time; // time in data loop number

// config
uint32_t GATE_mode, VCO_link, RINGMOD, VCF_pitch, sync_LFO1, cvg_type, MIX_type;

// env follower
uint32_t envelope;

// save
uint32_t flash_lock_bit;

#ifdef serialout
  // main Loop Counter bypasser
  uint16_t loopc=0;

  // for incoming serial data  
  //int incomingByte = 0;//maybe should be set to unsigned ? and why not use byte type !?
  byte incomingByte = 0xFF;
  byte incomingByte1 = 0; //when receiving an argument to the command (for instance 0xF1 0xFF ie. slowing down loop 255x)
  
  // main loop "jumper"
  // high value means slow or low resolution output
  // zero is maximum speed
  // but beware! when sending more than one continuous message
  // slowloop has to be raised to one (at least on the MMO-3)
  uint16_t slowloop=0;

  // shotgun
  // is were we save the type of message to send on the serial bus
  // shotgun[0] is were we save the type of non continuous message to send:
  // aka. knob value ([0x00,0x64(100)[), slower(0xF1)/speedier(0xF2) loop, identifier(0xF0), reinit(0xFF)
  // shotgun[1,2,3] is were we save the type of continuous message to send (>=0xA0 && <0xF0)
  byte shotgun[4];
  
  // keep track of still how much non continuous message has to be sent
  uint8_t shotguncounter=2;

  uint32_t VCO1_out, VCO2_out;
  int32_t MIX_out, VCF_out, VCA_out;

#endif

void setup() {
  uint32_t i;

  REG_PMC_PCER0 = 1 << 11; // enable la clock du port PIO A pour les entree
  REG_PMC_PCER0 = 1 << 12; // enable la clock du port PIO B pour les entree
  REG_PMC_PCER0 = 1 << 13; // enable la clock du port PIO C pour les entree
  REG_PMC_PCER0 = 1 << 14; // enable la clock du port PIO D pour les entree

  REG_SUPC_SMMR = 0x0000110B; // suply monitor reset at 3V
  REG_SUPC_MR = 0xA5005A00;

  init_dac();

  init_debug();
  init_led();
  init_analog_out();
  init_random();
  init_analog_in(); 
  init_keyboard();
  init_WF();
  init_midi();
  init_save();

  init_VCO();
  init_VCF();
  init_LFO1();
  init_LFO2();
  init_LFO3();
  init_CVG();
  init_ADSR();
  init_VCA();
  init_ENV();
  init_EFFECT();
  
  VCF_freq();
  VCO1_freq();
  VCO2_freq();
  PORTAMENTO_update();
  VCA_update();
  
  test(); // hardware test mode
 
  EFC0->EEFC_FMR = 0X00000400; // mandatory to keep program speed when loading the dueFlashStorage library. go wonder why.

  start_dac();

  #ifdef serialout
    //Serial.begin(9600);
    Serial.begin(115200);
    SerialUSB.begin(115200);
    Serial.println("Hey! Hey!");
    Serial.println("OCS-2!");
   #endif
  
  while (true) main_loop(); // do not go into arduino loop
}

inline void main_loop() { // as fast as possible
  uint32_t compteur, i, sound_in;
  uint32_t tmpU32;
  int32_t tmp32;
  
  
  #ifdef syncro_out
    test2_on();
  #endif
  analog_in();
  
  if (flash_lock_bit == 0) 
    keyboard_in();
  else
    if (efc_perform_command_is_ready(EFC1))
      save_conf0();
 
  WF_in();
  analog_start_1(); // start 1 sample
  VCO1_freq();
  VCO2_freq();
  VCF_freq();
  LFO3_freq();
  CVG_mod();
  LFO1_modulation();
  LFO2_modulation();
  LFO3_modulation();
  ENVELOPE_modulation();
  LFO1_freq();
  #ifdef syncro_out
    test2_off();
  #endif  
  analog_get_1(); // get 1 sample
  analog_start_1(); // start 2nd sample
  LFO2_freq();
  MIDI_in();
  PORTAMENTO_update(); 
  ADSR_update();
  VCA_update();
  EFFECT_update();
  update_leds(); // gate and midi leds
  update_ext(); // external analog value
  analog_get_1(); // 2nd sample
  
  #ifdef serialout
  
    if (SerialUSB.available() > 0) {
      //read the incoming byte:
      incomingByte = SerialUSB.read();
      /**/
      Serial.print("I received: ");
      Serial.println(incomingByte, DEC);
      /**/
      if ((incomingByte < 0xA0) || (incomingByte == 0xF0) || (incomingByte == 0xF1) || (incomingByte == 0xF2)){
        loopc=slowloop;
        shotguncounter=2;
        shotgun[0]=incomingByte;
      } else// if (incomingByte > 0) //pourquoi ce test ?! on n'envoie que des valeurs positives non ? on l'enlève ce 28/04/18
        if (incomingByte == 0xFF) {
          shotgun[0]=0xFF;
          shotgun[1]=0xFF;
          shotgun[2]=0xFF;
          shotgun[3]=0xFF;
          slowloop=0;
          Serial.print("Maximum shotgun speed set:");
          Serial.println(slowloop);
        }
        else { // continuous dump
         if (incomingByte ==  shotgun[1]) {
          shotgun[1]=shotgun[2];
          shotgun[2]=shotgun[3];
          shotgun[3]=0xFF;
          slowloop = ((shotgun[2] == 0xFF)) ? (slowloop == 1) ? 0 : slowloop : slowloop;
          Serial.print("Tweaking shotgun speed:");
          Serial.println(slowloop);
         }
         else {
          if (incomingByte == shotgun [2]) {
           shotgun[2]=shotgun[3];
           shotgun[3]=0xFF;
          }
          else {
           if (incomingByte == shotgun [3]) {
            shotgun[3]=0xFF;
           }
           else {
            shotgun[3]=shotgun[2];
            shotgun[2]=shotgun[1];
            shotgun[1]=incomingByte;             
//            slowloop = ((slowloop == 1) && (shotgun[2] == 0xFF)) ? 0 : !(slowloop) ? 1 : slowloop;
            slowloop = ((shotgun[2] != 0xFF)) ? (slowloop > 1) ? slowloop : 1 : (slowloop > 1) ? slowloop : 0;
            Serial.print("Tweaking shotgun speed:");
            Serial.println(slowloop);
           }
          }
         }
        }

  }
        
  if (!(loopc++ < slowloop)){
   loopc=0;
   if (incomingByte != 0xFF) {
//    for (i=0;i<4;i++){
//      switch (shotgun[i]) {
     if (shotgun[0] != 0xFF) {
        switch (shotgun[0]) {
        case 0:
        case 1:
        case 2:
        case 3:
        case 4:
        case 5:
        case 6:
        case 7:
        case 8:
        case 9:
        case 10:
        case 11:
        case 12:
        case 13:
        case 14:
        case 15:
        case 16:
        case 17:
        case 18:
        case 19:
        case 20:
        case 21:
        case 22:
        case 23:
        case 24:
        case 25:
        case 26:
        case 27:
        case 28:
        case 29:
        case 30:
        case 31:
        case 32:
        case 33:
        if (0 < shotguncounter) {
          SerialUSB.write(0xFF);
          SerialUSB.write((byte)shotgun[i]);
          SerialUSB.write(adc_value16[shotgun[i]] >>  8 & 0xFF);
          SerialUSB.write(adc_value16[shotgun[i]] >>  0 & 0xFF);
          shotguncounter--;
        } else {
          shotgun[0]=0xFF;
        }
        break;

        case 0xF0:
        if (0 < shotguncounter) {
          SerialUSB.write(0xFF);
          SerialUSB.write(0xF0);
          SerialUSB.print("O2");
          shotguncounter--;
        } else {
          shotgun[0]=0xFF;
        }
        break;
        
        case 0xF1:
        if (0 < shotguncounter) {
          if (!(SerialUSB.available() > 0))
            slowloop++;
            else {
              incomingByte1 = SerialUSB.read();
              slowloop += incomingByte1;
            }

        Serial.print("Slowing down shotgun:");
        Serial.println(slowloop);
        shotguncounter=0;
        } else {
          shotgun[0]=0xFF;
        }
        break;
        
        case 0xF2:
        if (0 < shotguncounter) {
          if (!(SerialUSB.available() > 0))
            slowloop = (1 < slowloop) ? --slowloop : (shotgun[2] == 0xFF) ? 0 : 1;
            else {
              incomingByte1 = SerialUSB.read();
              slowloop = (incomingByte1 < slowloop) ? (slowloop-incomingByte1) : (shotgun[2] == 0xFF) ? 0 : 1;
            }
        
        Serial.print("Speeding up shotgun:");
        Serial.println(slowloop);
        shotguncounter=0;
        } else {
          shotgun[0]=0xFF;
        }
        break;
       }
     }

      for (i=1;i<4;i++){
        switch (shotgun[i]) {

        case 0xA0://VCO1 1
        case 0xA1://VCO2 2
        case 0xA2://LFO1 3
        case 0xA3://LFO2 4
        case 0xA4://LFO3 5
        case 0xA5://CVGEN 6
        case 0xA6://ADSR 7
        case 0xA7://LIGHT 8
        case 0xA8://AUDIO IN 9
        case 0xA9://Midi (Keyboard ?) Velocity 10
        case 0xAA://CV1 11
        case 0xAB://CV2 12
        case 0xAC://CV3 13
        SerialUSB.write(0xFF);
        SerialUSB.write((byte)shotgun[i]);
        SerialUSB.write(modulation_data[shotgun[i]-0xA0] >>  8 & 0xFF);
        SerialUSB.write(modulation_data[shotgun[i]-0xA0] >>  0 & 0xFF);
        break;

        case 0xF3://17
        SerialUSB.write(0xFF);
        SerialUSB.write((byte)shotgun[i]);
        //SerialUSB.write(VCO1_out >>  24 & 0xFF);
        //SerialUSB.write(VCO1_out >>  16 & 0xFF);
        SerialUSB.write((VCO1_out / 65536) >>  8 & 0xFF);
        SerialUSB.write((VCO1_out / 65536) >>  0 & 0xFF);
        break;

        case 0xF4://18
        SerialUSB.write(0xFF);
        SerialUSB.write((byte)shotgun[i]);
        //SerialUSB.write(VCO2_out >>  24 & 0xFF);
        //SerialUSB.write(VCO2_out >>  16 & 0xFF);
        SerialUSB.write((VCO2_out / 65536) >>  8 & 0xFF);
        SerialUSB.write((VCO2_out / 65536) >>  0 & 0xFF);
        break;

        case 0xF6://20
        SerialUSB.write(0xFF);
        SerialUSB.write((byte)shotgun[i]);
        //SerialUSB.write(VCF_out >>  24 & 0xFF);
        //SerialUSB.write(VCF_out >>  16 & 0xFF);
        SerialUSB.write((VCF_out / 65536) >>  8 & 0xFF);
        SerialUSB.write((VCF_out / 65536) >>  0 & 0xFF);
        break;

        case 0xF7://21
        SerialUSB.write(0xFF);
        SerialUSB.write((byte)shotgun[i]);
        //SerialUSB.write(MIX_out >>  24 & 0xFF);
        //SerialUSB.write(MIX_out >>  16 & 0xFF);
        //SerialUSB.write((MIX_out / 65536) >>  8 & 0xFF);
        //SerialUSB.write((MIX_out / 65536) >>  0 & 0xFF);
        //à l'usage MIX_out ne semble pas être une valeur long mais plutot short
        //code have to be checked
        SerialUSB.write((MIX_out) >>  8 & 0xFF);
        SerialUSB.write((MIX_out) >>  0 & 0xFF);
        break;

        case 0xF8://22
        SerialUSB.write(0xFF);
        SerialUSB.write((byte)shotgun[i]);
        //SerialUSB.write(VCA_out >>  24 & 0xFF);
        //SerialUSB.write(VCA_out >>  16 & 0xFF);
        SerialUSB.write((VCA_out / 65536) >>  8 & 0xFF);
        SerialUSB.write((VCA_out / 65536) >>  0 & 0xFF);
        break;

        }
      }
    }
  }
  
  #endif
}

void loop() {
  //not used
}

inline void compute_audio_sample() {

#ifndef serialout
  uint32_t VCO1_out, VCO2_out;
  int32_t MIX_out, VCF_out, VCA_out;
#endif
  
  PORTAMENTO();                               // 0.1 µs
  VCO1_out = VCO1();                          // 2.9 µs
  VCO2_out = VCO2();                          // 2.9 µs
  MIX_out = MIX(VCO1_out, VCO2_out);          // 0.8 µs
  VCF_out = VCF(MIX_out);                     // 2.4 µs
  ADSR();                                     // 0.1 µs
  VCA_out = EFFECT(VCF_out);                  // 0.8 µs

  // modulation signal
  LFO1();         // 0.4 µs 
  LFO2();         // 0.4 µs
  LFO3();         // 0.4 µs
  ENVELOPE();     // 0.4 µs
 
  audio_out = VCA_out;
}

void SSC_Handler(void){
  
  #ifdef syncro_out
    test1_on();
  #endif
  
  if (!(REG_SSC_SR & (1<<10))) {
    REG_SSC_THR = REG_SSC_RHR; // just to initialise properlly (not to invert R and L)
    NVIC_ClearPendingIRQ(SSC_IRQn); // next sample is allready here, no need to go to an other interuption to get it (it save time)
  }
  else {
    audio_inL = REG_SSC_RHR;
    REG_SSC_THR = audio_out2;
    audio_out2 = audio_out; // Why is that mandatory to have the L and R in sync???
    
    compute_audio_sample();
    
    while(!(REG_SSC_SR & (1<<4))) {} // wait for the next sample to be ready (it should mostlly be here, but somtimes not)
    NVIC_ClearPendingIRQ(SSC_IRQn); // next sample is allready here, no need to go to an other interuption to get it (it save time)
    
    audio_inR = audio_inR2; // to get the L and R in phase
    audio_inR2 = REG_SSC_RHR;
    REG_SSC_THR = audio_out;
  }
  #ifdef syncro_out
    test1_off();
  #endif 
}


