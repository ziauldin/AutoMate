"use client"

import Image from "next/image"

interface ImageModalProps {
  isOpen: boolean
  onClose: () => void
  imageUrl?: string
}

export default function ImageModal({ isOpen, onClose, imageUrl = "/placeholder.svg" }: ImageModalProps) {
  return (
    <div className={`modal ${isOpen ? "active" : ""}`}>
      <div className="modal-content">
        <div className="modal-header">
          <h3>Image Analysis</h3>
          <button className="close-modal-btn" onClick={onClose}>
            <i className="fas fa-times"></i>
          </button>
        </div>
        <div className="modal-body">
          <div className="image-preview-container">
            <Image id="image-preview" src={imageUrl || "/placeholder.svg"} alt="Preview" width={600} height={400} />
          </div>
          <div className="image-analysis-result">{/* Analysis results will be added dynamically */}</div>
        </div>
      </div>
    </div>
  )
}
