"use client"

interface ComparisonModalProps {
  isOpen: boolean
  onClose: () => void
}

export default function ComparisonModal({ isOpen, onClose }: ComparisonModalProps) {
  return (
    <div className={`modal ${isOpen ? "active" : ""}`}>
      <div className="modal-content">
        <div className="modal-header">
          <h3>Car Comparison</h3>
          <button className="close-modal-btn" onClick={onClose}>
            <i className="fas fa-times"></i>
          </button>
        </div>
        <div className="modal-body">
          <div className="comparison-container">{/* Comparison content will be added dynamically */}</div>
        </div>
      </div>
    </div>
  )
}
