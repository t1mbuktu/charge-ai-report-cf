from solarForecastService import SolarForecastService as sfs
from datetime import datetime
import json 

class ChargingPlanService:
    
    @staticmethod
    def create_simple_charging_plan(sim_data, solar_forecast, cars, settings):
        returnData = {
            "solarPowerUsed_per": None,
            "solarForecast": None,
            "gridPowerUsed_kwh": 0,
            "solarPowerUsed_kwh": 0,
            "chargeForecast": [],
        }
        # Erstellen eines Array welches fuer jede Stude die prognostizierte Solar-Leistung enthaelt
        solarEnergyForecast = []
        for forecast in solar_forecast:
            solarEnergyForecast.append([forecast["dateAndTime"], sfs.calculate_solar_power(forecast["solarRadiation"], settings)])
        
        returnData["solarForecast"] = list(map((lambda x: {"date": x[0], "speed_kwh": x[1]}), solarEnergyForecast))
        
        #Summe der prognositizierten Solar - Produktion
        sumSolarTotal = sum(item[1] for item in solarEnergyForecast)
        
        # fuer jedes Auto
        for car in cars:
            # fuer die entsprechenden Simulationsdaten des Autos
            for car_sim in sim_data:
                if(car_sim["carId"] == car["id"]):
                    # Aufbau chargingPlan [[Datum und Uhrzeit, Speed Solar, Speed Grid, Battery LvL kwh, Battery Lvl % ],...]
                    chargingPlan = list(map((lambda x: [x[0], None, None, None, None, x[1]]), solarEnergyForecast))
                    chargeTimeStart = datetime.strptime(solarEnergyForecast[0][0], '%Y-%m-%dT%H:%M')
                    batteryLevel_kwh = car["batteryCapacity"] * car["chargeLimit"] * car["batteryLevel"]
                    batteryLevel_per = batteryLevel_kwh / car["batteryCapacity"]
                    energyNeeded = car["batteryCapacity"] * car["chargeLimit"] - batteryLevel_kwh
                                        
                    # fuer jeden Abwesendheits-Slot
                    for sim in car_sim["data"]:
                        arrival = datetime.strptime(sim["to"], '%Y-%m-%dT%H:%M')
                        departure = datetime.strptime(sim["from"], '%Y-%m-%dT%H:%M')
                        duration_hours = (departure - chargeTimeStart).total_seconds() / 3600
                        total_solar_power = 0
                        total_grid_power = 0 
                        
                        for i, eForecast in enumerate(solarEnergyForecast):
                            if chargeTimeStart <= datetime.strptime(eForecast[0], '%Y-%m-%dT%H:%M') < departure:
                                maxCharging = car["maxChargeSpeed"]
                                if(energyNeeded >= maxCharging):
                                    solarConsume = min(maxCharging, eForecast[1])
                                    gridConsume = maxCharging - solarConsume
                                else:
                                    solarConsume = min(energyNeeded, eForecast[1])
                                    gridConsume = energyNeeded - solarConsume
                                
                            
                                eForecast[1] -= solarConsume # genutzte Solarleistung abziehen
                                energyNeeded -= (solarConsume + gridConsume)
                                chargingPlan[i][1] = solarConsume #solar Power
                                chargingPlan[i][2] = gridConsume #grid Power 
                                chargingPlan[i][3] = batteryLevel_kwh #battery level in kwh
                                chargingPlan[i][4] = batteryLevel_per # battery level in %
                                chargingPlan[i][1] = solarConsume
                                batteryLevel_kwh += solarConsume + gridConsume
                                returnData["solarPowerUsed_kwh"] += solarConsume
                                returnData["gridPowerUsed_kwh"] += gridConsume
                                
                            #zu der Zeit wo das Auto nicht da ist, ist sowohl solar als auch grid speed bei 0
                            elif departure <= datetime.strptime(eForecast[0], '%Y-%m-%dT%H:%M') < arrival:
                                chargingPlan[i][1] = None #solar power
                                chargingPlan[i][2] = None #grid power
                                        
                        chargeTimeStart = arrival
                        batteryLevel_kwh = car["batteryCapacity"] * sim["batteryLevel"]
                        batteryLevel_per = batteryLevel_kwh / car["batteryCapacity"]
                        energyNeeded = car["batteryCapacity"] * car["chargeLimit"] - batteryLevel_kwh
                        
            returnData["chargeForecast"].append({    
                "carId": car["id"],
                "data": list(map((lambda x: {
                    "date": x[0],
                    "chargingSpeedSolar": x[1], 
                    "chargingSpeedGrid": x[2], 
                    "batteryLevel_kwh": x[3], 
                    "batteryLevel_per": x[4],
                    "solarForecast": x[5]
                }), chargingPlan))
            })
            
        solarEnergyUsed_per = returnData["solarPowerUsed_kwh"] / sumSolarTotal
        returnData["solarPowerUsed_per"] = solarEnergyUsed_per
        
        return returnData
    
    @staticmethod
    def create_smart_charging_plan(sim_data, solar_forecast, cars, settings):
        returnData = {
            "solarPowerUsed_per": None,
            "solarForecast": None,
            "gridPowerUsed_kwh": 0,
            "solarPowerUsed_kwh": 0,
            "chargeForecast": [],
        }
        # Erstellen eines Array welches fuer jede Stude die prognostizierte Solar-Leistung enthaelt
        solarEnergyForecast = []
        for forecast in solar_forecast:
            solarEnergyForecast.append([forecast["dateAndTime"], sfs.calculate_solar_power(forecast["solarRadiation"], settings)])
        
        returnData["solarForecast"] = list(map((lambda x: {"date": x[0], "speed_kwh": x[1]}), solarEnergyForecast))
        
        #Summe der prognositizierten Solar - Produktion
        sumSolarTotal = sum(item[1] for item in solarEnergyForecast)
        
        # fuer jedes Auto
        for car in cars:
            # fuer die entsprechenden Simulationsdaten des Autos
            for car_sim in sim_data:
                if(car_sim["carId"] == car["id"]):
                    # Aufbau chargingPlan [[Datum und Uhrzeit, Speed Solar, Speed Grid, Battery LvL kwh, Battery Lvl %, Solar Forecast],...]
                    chargingPlan = list(map((lambda x: [x[0], None, None, None, None, x[1]]), solarEnergyForecast))
                    chargeTimeStart = datetime.strptime(solarEnergyForecast[0][0], '%Y-%m-%dT%H:%M')
                    batteryLevel_kwh = car["batteryCapacity"] * car["chargeLimit"] * car["batteryLevel"]
                    batteryLevel_per = batteryLevel_kwh / car["batteryCapacity"]
                    energyNeeded = car["batteryCapacity"] * car["chargeLimit"] - batteryLevel_kwh
                    
                    # fuer jeden Abwesendheits-Slot
                    for sim in car_sim["data"]:
                        arrival = datetime.strptime(sim["to"], '%Y-%m-%dT%H:%M')
                        departure = datetime.strptime(sim["from"], '%Y-%m-%dT%H:%M')
                        
                        # Berechnen der Solarleistung bis zur naechsten Abfahrt
                        for i, eForecast in enumerate(solarEnergyForecast):
                            if chargeTimeStart <= datetime.strptime(eForecast[0], '%Y-%m-%dT%H:%M') < departure:
                                
                                # forecast[1] enstpricht der Solarleistung in der Stunde                             
                                if(eForecast[1] > energyNeeded):
                                    solarConsume = energyNeeded
                                else:
                                    solarConsume = eForecast[1]
                                    
                                eForecast[1] -= solarConsume  
                                chargingPlan[i][1] = solarConsume
                                energyNeeded -= solarConsume
                                returnData["solarPowerUsed_kwh"] += solarConsume
                                
                        #Auffuellen des Plans mit Grid Power, sollte Solar nicht gereicht haben
                        for i, eForecast in enumerate(solarEnergyForecast):
                            if chargeTimeStart <= datetime.strptime(eForecast[0], '%Y-%m-%dT%H:%M') < departure:
                                solarConsume = chargingPlan[i][1]
                                gridConsumable = car["maxChargeSpeed"] - int(solarConsume)
                                
                                if(gridConsumable > energyNeeded):
                                    gridConsume = energyNeeded
                                else:
                                    gridConsume = gridConsumable                                  
                                
                                chargingPlan[i][2] = gridConsume #grid Power 
                                chargingPlan[i][3] = batteryLevel_kwh #battery lelvel in kwh
                                chargingPlan[i][4] = batteryLevel_per # battery level in %
                                returnData["gridPowerUsed_kwh"] += gridConsume
                                
                                batteryLevel_kwh += solarConsume + gridConsume
                                energyNeeded -= gridConsume
                            
                            #zu der Zeit wo das Auto nicht da ist, ist sowohl solar als auch grid speed bei 0
                            elif departure <= datetime.strptime(eForecast[0], '%Y-%m-%dT%H:%M') < arrival:
                                chargingPlan[i][1] = None #solar power
                                chargingPlan[i][2] = None #grid power                         
                        
                        chargeTimeStart = arrival
                        batteryLevel_kwh = car["batteryCapacity"] * sim["batteryLevel"]
                        batteryLevel_per = batteryLevel_kwh / car["batteryCapacity"]
                        energyNeeded = car["batteryCapacity"] * car["chargeLimit"] - batteryLevel_kwh

            returnData["chargeForecast"].append({    
                "carId": car["id"],
                "data": list(map((lambda x: {
                    "date": x[0], 
                    "chargingSpeedSolar": x[1], 
                    "chargingSpeedGrid": x[2], 
                    "batteryLevel_kwh": x[3], 
                    "batteryLevel_per": x[4],
                    "solarForecast": x[5]
                }), chargingPlan))
            })
            
        solarEnergyUsed_per = returnData["solarPowerUsed_kwh"] / sumSolarTotal
        returnData["solarPowerUsed_per"] = solarEnergyUsed_per
        
        return returnData
    
    @staticmethod
    def getReport(sim_data, cars, settings):
        latitude = settings["location"]["latitude"]
        longitude = settings["location"]["longitude"]
        solar_forecast = sfs.get_solar_forecast(latitude, longitude)
        
        data_smart = ChargingPlanService.create_smart_charging_plan(sim_data, solar_forecast, cars, settings)
        data_simple = ChargingPlanService.create_simple_charging_plan(sim_data, solar_forecast, cars, settings)
        solar_forecast = data_smart["solarForecast"]
        
        del data_smart["solarForecast"]
        del data_simple["solarForecast"]
        
        returnData = {
            "diffGridPowerUsed_kwh": data_smart["gridPowerUsed_kwh"] - data_simple["gridPowerUsed_kwh"],
            "diffGridPowerUsed_per": (data_smart["solarPowerUsed_per"] - data_simple["solarPowerUsed_per"]) - 1,
            "diffSolarPowerUsed_kwh": data_smart["solarPowerUsed_kwh"] - data_simple["solarPowerUsed_kwh"],
            "diffSolarPowerUsed_per": data_smart["solarPowerUsed_per"] - data_simple["solarPowerUsed_per"],
            "simpleChargingForecast": data_simple,
            "smartChargingForecast": data_smart,
            "solarForecast": solar_forecast
        }
        
        return returnData
    
    @staticmethod
    def getJSONReport(sim_data, cars, settings):
        reportAsDict = ChargingPlanService.getReport(sim_data, cars, settings)
        return json.dumps(reportAsDict)