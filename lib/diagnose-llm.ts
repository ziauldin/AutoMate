export class CarDiagnosisChat {
    private apiKey: string
    private conversationHistory: Array<{ role: string; content: string }>
    private carDetails: any
    private diagnosis_complete: boolean
    private car_images: Record<string, Record<string, string>>
  
    constructor() {
      this.apiKey = process.env.GROQ_API_KEY || "demo_key" // Fallback to demo mode
      this.conversationHistory = []
      this.carDetails = null
      this.diagnosis_complete = false
      this.car_images = this._loadCarImages()
    }
  
    private _loadCarImages(): Record<string, Record<string, string>> {
      // In a real app, this would come from a database
      // For demo purposes, we'll use a hardcoded dictionary
      return {
        Toyota: {
          Corolla: "/static/images/cars/toyota-corolla.jpg",
          Camry: "/static/images/cars/toyota-camry.jpg",
          RAV4: "/static/images/cars/toyota-rav4.jpg",
          Prius: "/static/images/cars/toyota-prius.jpg",
          Highlander: "/static/images/cars/toyota-highlander.jpg",
        },
        Honda: {
          Civic: "/static/images/cars/honda-civic.jpg",
          Accord: "/static/images/cars/honda-accord.jpg",
          "CR-V": "/static/images/cars/honda-crv.jpg",
          Pilot: "/static/images/cars/honda-pilot.jpg",
          Odyssey: "/static/images/cars/honda-odyssey.jpg",
        },
        // Add more manufacturers and models as needed
      }
    }
  
    public setCarDetails(manufacturer: string, model: string, year: number): any {
      this.carDetails = {
        manufacturer,
        model,
        year,
      }
  
      const welcomeMsg =
        `Thank you for selecting your ${year} ${manufacturer} ${model}. ` +
        "I'm your virtual assistant and can help with information about your vehicle. " +
        "What would you like to know about your car?"
  
      this.conversationHistory.push({ role: "assistant", content: welcomeMsg })
  
      // Get car image if available
      const carImage = this._getCarImage(manufacturer, model)
  
      return {
        message: welcomeMsg,
        car_image: carImage,
        car_details: this.carDetails,
      }
    }
  
    private _getCarImage(manufacturer: string, model: string): string | null {
      if (manufacturer in this.car_images && model in this.car_images[manufacturer]) {
        return this.car_images[manufacturer][model]
      }
  
      // Return a default placeholder if specific image not found
      return `/placeholder.svg?make=${manufacturer}&model=${model}`
    }
  
    public async getDiagnosis(userInput: string): Promise<any> {
      if (!this.carDetails) {
        return { message: "Please provide car details first" }
      }
  
      // Add user message to history
      this.conversationHistory.push({ role: "user", content: userInput })
  
      // Check if user is asking to see the car
      const showCar = this._isAskingForCarImage(userInput)
  
      // In demo mode or if API key is not available, use predefined responses
      if (!this.apiKey || this.apiKey === "demo_key") {
        const response = this._getDemoResponse(userInput, showCar)
        this.conversationHistory.push({ role: "assistant", content: response.message })
        return response
      }
  
      // For real LLM integration (when API key is available)
      try {
        // This would be the real LLM integration
        // For now, we'll just use the demo response
        const response = this._getDemoResponse(userInput, showCar)
        this.conversationHistory.push({ role: "assistant", content: response.message })
        return response
      } catch (error) {
        console.error("Error getting diagnosis:", error)
        const response = this._getDemoResponse(userInput, showCar)
        this.conversationHistory.push({ role: "assistant", content: response.message })
        return response
      }
    }
  
    private _isAskingForCarImage(userInput: string): boolean {
      const keywords = ["show car", "see car", "car image", "picture", "photo", "what does it look like"]
      return keywords.some((keyword) => userInput.toLowerCase().includes(keyword))
    }
  
    private _getDemoResponse(userInput: string, showCar = false): any {
      const userInputLower = userInput.toLowerCase()
      const { manufacturer, model, year } = this.carDetails
  
      // Check for specific queries
      if (showCar) {
        return {
          message: `Here's your ${year} ${manufacturer} ${model}:`,
          car_image: this._getCarImage(manufacturer, model),
        }
      }
  
      if (this._containsAny(userInputLower, ["specs", "specifications", "features"])) {
        return {
          message:
            `The ${year} ${manufacturer} ${model} comes with the following specifications:\n\n` +
            `• Engine: 2.5L 4-cylinder\n` +
            `• Horsepower: 203 hp\n` +
            `• Torque: 184 lb-ft\n` +
            `• Transmission: 8-speed automatic\n` +
            `• Fuel Economy: 28 city / 39 highway mpg\n` +
            `• Safety: 5-star crash rating`,
          car_image: null,
        }
      }
  
      if (this._containsAny(userInputLower, ["price", "cost", "how much"])) {
        return {
          message:
            `The ${year} ${manufacturer} ${model} has a starting MSRP of $27,995. ` +
            `Would you like to know about available trim levels and their pricing?`,
          car_image: null,
        }
      }
  
      if (this._containsAny(userInputLower, ["color", "colors", "available in"])) {
        return {
          message:
            `The ${year} ${manufacturer} ${model} is available in the following colors: ` +
            `Midnight Black, Platinum White, Celestial Silver, Blueprint Blue, Ruby Flare, and Supersonic Red.`,
          car_image: null,
        }
      }
  
      if (this._containsAny(userInputLower, ["maintenance", "service"])) {
        this.diagnosis_complete = true
        return {
          message:
            `For the ${year} ${manufacturer} ${model}, we recommend the following maintenance schedule:\n\n` +
            `• Oil change: Every 5,000 miles\n` +
            `• Tire rotation: Every 5,000 miles\n` +
            `• Brake inspection: Every 10,000 miles\n` +
            `• Air filter: Every 15,000 miles\n` +
            `• Major service: Every 30,000 miles`,
          car_image: null,
        }
      }
  
      // Default responses
      const responses = [
        `I'm here to help with any questions about your ${year} ${manufacturer} ${model}. What would you like to know?`,
        `The ${year} ${manufacturer} ${model} is an excellent choice! How can I assist you with it today?`,
        `I can provide information about specifications, features, pricing, and maintenance for your ${year} ${manufacturer} ${model}. What are you interested in?`,
        `Thank you for your message. Is there anything specific about the ${year} ${manufacturer} ${model} you'd like to learn more about?`,
      ]
  
      return {
        message: responses[Math.floor(Math.random() * responses.length)],
        car_image: null,
      }
    }
  
    private _containsAny(text: string, keywords: string[]): boolean {
      return keywords.some((keyword) => text.includes(keyword))
    }
  
    public extractRecommendationKeywords(): string[] {
      if (!this.diagnosis_complete) {
        return []
      }
  
      const commonParts = [
        "oil",
        "filter",
        "brake",
        "pad",
        "rotor",
        "battery",
        "alternator",
        "spark plug",
        "ignition",
        "radiator",
        "thermostat",
        "belt",
        "hose",
        "gasket",
        "sensor",
      ]
  
      const keywords: string[] = []
      for (const message of this.conversationHistory) {
        if (message.role === "assistant") {
          const content = message.content.toLowerCase()
          for (const part of commonParts) {
            if (content.includes(part) && !keywords.includes(part)) {
              keywords.push(part)
            }
          }
        }
      }
  
      return keywords
    }
  }
  