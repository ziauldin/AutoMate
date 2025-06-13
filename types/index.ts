export interface CarData {
    [manufacturer: string]: string[]
  }
  
  export interface CarDetails {
    manufacturer: string
    model: string
    year: number
  }
  
  export interface Message {
    content: string
    role: "user" | "assistant"
    timestamp: string
    car_image?: string
    products?: Product[]
  }
  
  export interface Product {
    title: string
    price: number
    category: string
  }
  
  export interface Session {
    id: string
    car_details: CarDetails
    created_at: string
    last_message: string
    message_count: number
  }
  