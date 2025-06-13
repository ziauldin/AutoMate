import React, { useState } from "react"

interface WelcomeScreenProps {
  onStartChat: (manufacturer: string, model: string, year: number) => void
}

const WelcomeScreen: React.FC<WelcomeScreenProps> = ({ onStartChat }) => {
  const [step, setStep] = useState<"manufacturer" | "model" | "year">("manufacturer")
  const [manufacturer, setManufacturer] = useState("")
  const [model, setModel] = useState("")
  const [year, setYear] = useState("")

  const manufacturers = ["Toyota", "Honda", "Ford", "Chevrolet", "BMW"]
  const models = ["Model 1", "Model 2", "Model 3"]
  const years = ["2023", "2022", "2021"]

  const handleManufacturerSelect = (m: string) => {
    setManufacturer(m)
    setStep("model")
  }

  const handleModelSelect = (m: string) => {
    setModel(m)
    setStep("year")
  }

  const handleYearSelect = (y: string) => {
    setYear(y)
    onStartChat(manufacturer, model, parseInt(y))
  }

  return (
    <div className="welcome-screen">
      <div className="welcome-container">
        <div className="welcome-header">
          <div className="logo large">
            <i className="fas fa-car-alt"></i>
            <span>AutoGenius</span>
          </div>
          <p className="welcome-subtitle">AI-powered vehicle diagnostics</p>
        </div>

        <div className="welcome-card">
          <div className="navigation-steps">
            <div className={`step ${step === "manufacturer" ? "active" : ""}`}>
              <span className="step-number">1</span>
              <span className="step-label">Manufacturer</span>
            </div>
            <div className={`step ${step === "model" ? "active" : ""}`}>
              <span className="step-number">2</span>
              <span className="step-label">Model</span>
            </div>
            <div className={`step ${step === "year" ? "active" : ""}`}>
              <span className="step-number">3</span>
              <span className="step-label">Year</span>
            </div>
          </div>

          {step === "manufacturer" && (
            <div className="selection-grid">
              <h3 className="selection-title">Select Manufacturer</h3>
              <div className="grid-container">
                {manufacturers.map(m => (
                  <div key={m} className="grid-item" onClick={() => handleManufacturerSelect(m)}>
                    {m}
                  </div>
                ))}
              </div>
            </div>
          )}

          {step === "model" && (
            <div className="selection-grid">
              <h3 className="selection-title">Select Model</h3>
              <div className="grid-container">
                {models.map(m => (
                  <div key={m} className="grid-item" onClick={() => handleModelSelect(m)}>
                    {m}
                  </div>
                ))}
              </div>
            </div>
          )}

          {step === "year" && (
            <div className="selection-grid">
              <h3 className="selection-title">Select Year</h3>
              <div className="grid-container years-grid">
                {years.map(y => (
                  <div key={y} className="grid-item" onClick={() => handleYearSelect(y)}>
                    {y}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default WelcomeScreen