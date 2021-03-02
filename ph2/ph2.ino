/*
 # Based on the code written by
 # Editor : YouYou
 # Ver    : 1.0
 # Product: analog pH meter
 # SKU    : SEN0161
 # Modified by Daniele Dondi
*/
#define SensorPin A0            //pH meter Analog output to Arduino Analog Input 0
#define Sensor2Pin A1            //ORP combined electrode Analog output to Arduino Analog Input 1
#define LED 13
#define samplingInterval 20
#define printInterval 1000
#define ArrayLenth  40    //times of collection
int pHArray[ArrayLenth];   //Store the average value of the sensor feedback
int pHArray2[ArrayLenth];   //Store the average value of the sensor feedback
int pHArrayIndex=0;    
long tempo;
void setup(void)
{
  pinMode(LED,OUTPUT);  
  Serial.begin(9600);  
  Serial.println("RadChemLab Connected");    //Test the serial monitor
  Serial.println("Time (s)\t Voltage (V)\t Voltage2 (V)");    //Test the serial monitor  
  tempo=0;
}
void loop(void)
{
  static unsigned long samplingTime = millis();
  static unsigned long printTime = millis();
  static float pHValue,voltage,voltage2;
  if(millis()-samplingTime > samplingInterval)
  {
      pHArrayIndex++;
      pHArray[pHArrayIndex]=analogRead(SensorPin);
      pHArray2[pHArrayIndex]=analogRead(Sensor2Pin);      
      if(pHArrayIndex>=ArrayLenth)pHArrayIndex=0;
      voltage = avergearray(pHArray, ArrayLenth)*5.0/1024;
      voltage2 = avergearray(pHArray2, ArrayLenth)*5.0/1024;      
      samplingTime=millis();
  }
  if(millis() - printTime > printInterval)   //Every printinterval milliseconds, print a numerical, convert the state of the LED indicator
  {
        tempo++;
        Serial.print(tempo);
        Serial.print("\t");        
        Serial.print(voltage,4);
        Serial.print("\t");        
        Serial.println(voltage2,4);        
        digitalWrite(LED,digitalRead(LED)^1);
        printTime=millis();
  }
}
double avergearray(int* arr, int number){
  int i;
  int max,min;
  double avg;
  long amount=0;
  if(number<=0){
    Serial.println("Error number for the array to averaging!\n");
    return 0;
  }
  if(number<5){   //less than 5, calculated directly statistics
    for(i=0;i<number;i++){
      amount+=arr[i];
    }
    avg = amount/number;
    return avg;
  }else{
    if(arr[0]<arr[1]){
      min = arr[0];max=arr[1];
    }
    else{
      min=arr[1];max=arr[0];
    }
    for(i=2;i<number;i++){
      if(arr[i]<min){
        amount+=min;        //arr<min
        min=arr[i];
      }else {
        if(arr[i]>max){
          amount+=max;    //arr>max
          max=arr[i];
        }else{
          amount+=arr[i]; //min<=arr<=max
        }
      }//if
    }//for
    avg = (double)amount/(number-2);
  }//if
  return avg;
}
