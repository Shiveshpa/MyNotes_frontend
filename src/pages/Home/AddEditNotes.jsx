import React, { useState } from "react"
import { MdClose } from "react-icons/md"
import TagInput from "../../components/Input/TagInput "
import axios from "axios"
import { toast } from "react-toastify"
import { ThreeDots } from "react-loader-spinner";
import config from '../../config/config';
const apiUrl = config.API_URL;

const AddEditNotes = ({ onClose, noteData, type, getAllNotes }) => {
  const [title, setTitle] = useState(noteData?.title || "")
  const [content, setContent] = useState(noteData?.content || "")
  const [tags, setTags] = useState(noteData?.tags || [])
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false);

  //   Edit Note
const editNote = async () => {
  const noteId = noteData._id;  // The ID of the note to be edited
  console.log(noteId);

  const token = localStorage.getItem("access_token");

  if (!token) {
    console.log("No token found");
    setError("You must be logged in to edit a note");
    toast.error("You must be logged in to edit a note");
    return;
  }
  setLoading(true);

  try {
    const noteData = {
      title: title,      // Title of the note
      content: content,  // Content of the note
      tags: tags         // Tags of the note (assuming tags is an array or string)
    };

    // Make the PUT request with the token in the Authorization header
    const res = await axios.put(
      `${apiUrl}/edit?note_id=${noteId}`,  // Backend route to edit a note, passing note_id as a query parameter
      noteData,  // Send the updated note data in the body of the request
      {
        headers: {
          "Content-Type": "application/json",  // Ensure the content type is JSON
          "Authorization": `Bearer ${token}`   // Pass the token in the Authorization header
        }
      }
    );

    console.log(res.data);

    if (res.data.success === false) {
      console.log(res.data.message);
      setError(res.data.message);
      toast.error(res.data.message);
      return;
    }

    toast.success(res.data.message);
    getAllNotes();  // Refresh the list of notes after editing
    onClose();      // Close the edit note modal or dialog
  } catch (error) {
    toast.error(error.message);
    console.log(error.message);
    setError(error.message);
  }finally {
    setLoading(false);
  }
};

  //   Add Note
  const addNewNote = async () => {
    try {
      // Get token from localStorage
      const token = localStorage.getItem("access_token");
    
      if (!token) {
        console.log("No token found");
        setError("You must be logged in to add a note");
        toast.error("You must be logged in to add a note");
        return;
      }
    
      // Prepare the note data
      const noteData = {
        title: title,      // Title of the note
        content: content,  // Content of the note
        tags: tags         // Tags of the note (assuming tags is an array or string)
      };
      setLoading(true)
  
      // Make the POST request with the token in the Authorization header
      const res = await axios.post(
        `${apiUrl}/add`,  // Backend route to add a new note
        noteData,  // Send the note data in the body of the request
        {
          headers: {
            "Content-Type": "application/json",  // Ensure the content type is JSON
            "Authorization": `Bearer ${token}`   // Pass the token in the Authorization header
          }
        }
      );
  
      // Check the response for success or failure
      if (res.data.success === false) {
        console.log(res.data.message);
        setError(res.data.message);
        toast.error(res.data.message);
        return;
      }
  
      // Notify success
      toast.success(res.data.message);
      getAllNotes();  // Fetch updated notes after adding the new one
      onClose();  // Close the modal or reset the state
    } catch (error) {
      // Handle errors
       toast.error(error.message);
      console.log(error.message);
      setError(error.message);
    }
    finally{
      setLoading(false)
    }
  };
  
  

  const handleAddNote = () => {
    if (!title) {
      setError("Please enter the title")
      return
    }

    if (!content) {
      setError("Please enter the content")
      return
    }

    setError("")

    if (type === "edit") {
      editNote()
    } else {
      addNewNote()
    }
  }

  return (
    <div className="relative">
      <button
        className="w-10 h-10 rounded-full flex items-center justify-center absolute -top-3 -right-3 hover:bg-slate-50"
        onClick={onClose}
      >
        <MdClose className="text-xl text-slate-400" />
      </button>
      <div className="flex flex-col gap-2">
        <label className="input-label text-red-400 uppercase">Title</label>

        <input
          type="text"
          className="text-2xl text-slate-950 outline-none"
          placeholder="Wake up at 6 a.m."
          value={title}
          onChange={({ target }) => setTitle(target.value)}
        />
      </div>
      <div className="flex flex-col gap-2 mt-4">
        <label className="input-label text-red-400 uppercase">Content</label>

        <textarea
          type="text"
          className="text-sm text-slate-950 outline-none bg-slate-50 p-2 rounded"
          placeholder="Content..."
          rows={10}
          value={content}
          onChange={({ target }) => setContent(target.value)}
        />
      </div>

      <div className="mt-3">
        <label className="input-label text-red-400 uppercase">tags</label>
        <TagInput tags={tags} setTags={setTags} />
      </div>

      {error && <p className="text-red-500 text-xs pt-4">{error}</p>}

      <button
      className="btn-primary font-medium mt-5 p-3"
      onClick={handleAddNote}
      disabled={loading}  // Disable the button while loading
    >
      {loading ? (
        <ThreeDots color="#3498db" height={20} width={20} /> // Add the loader component here
      ) : (
        type === "edit" ? "UPDATE" : "ADD"
      )}
    </button>

    </div>
  )
}

export default AddEditNotes
