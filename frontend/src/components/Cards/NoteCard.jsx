import React, { useState } from "react";
import { FaTags } from "react-icons/fa6"
import { MdCreate, MdDelete, MdOutlinePushPin,MdSummarize , MdClose} from "react-icons/md"
import moment from "moment"


const NoteCard = ({
  title,
  date,
  content,
  tags,
  summary,
  isPinned,
  onPinNote,
  onEdit,
  onDelete,
}) => {
  const [showModal, setShowModal] = useState(false);// State to toggle summary

  const handleToggleSummary = () => {
    setShowModal((prev) => !prev); // Toggle modal visibility
  };

  const handleCloseModal = () => {
    setShowModal(false); // Close the modal
  };
  return (
    <div className="border rounded p-4 bg-indigo-100 border-indigo-300 hover:bg-indigo-130 hover:shadow-xl transition-all ease-in-out">
      <div className="flex items-center justify-between">
        <div>
          <h6 className="text-sm font-medium">{title}</h6>
          <span className="text-xs text-green-700">
            {moment(date).format("Do MMM YYYY")}
          </span>
        </div>
        

        {/* <MdOutlinePushPin
          className={`icon-btn ${
            isPinned ? "text-[#2B85FF] " : "text-slate-300"
          }`}
          onClick={onPinNote}
        /> */}
        <MdSummarize
          className="icon-btn text-slate-500 hover:text-blue-500"
          onClick={handleToggleSummary}
          title={showModal ? "Close Summary" : "Show Summary"} // Change tooltip dynamically
        />
      </div>

      {/* Toggle between content and summary */}
      {/* <p className="text-xs text-slate-600 mt-2">{showSummary ? summary : content?.slice(0, 60)} Show summary if toggled</p> */}
      <p className="text-xs text-slate-600 mt-2">{content?.slice(0, 200)}</p>
      <div className="flex items-center justify-between mt-2">
        <div className="text-xs text-slate-500">
          {tags.map((item) => `#${item} `)}
        </div>

        <div className="flex items-center gap-2">
          <MdCreate
            className="icon-btn hover:text-green-600"
            onClick={onEdit}
          />

          <MdDelete
            className="icon-btn hover:text-red-500"
            onClick={onDelete}
          />
        </div>
      </div>
      {showModal && (
        <div className="fixed inset-0 bg-gray-800 bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded shadow-lg relative w-3/4 md:w-1/2">
            <div className="flex items-center justify-between">
              <h6 className="text-sm font-medium text-blue-600">Summary</h6>
              <MdClose
                className="icon-btn text-gray-500 hover:text-red-500"
                onClick={handleCloseModal}
              />
            </div>
            <p className="text-xs text-slate-600 mt-4">{summary}</p>
          </div>
        </div>
      )}
    </div>
  )
}

export default NoteCard
