import { useState } from "react";
import { Card, CardContent } from "./ui/card";
import { Input } from "./ui/input";
import { Button } from "./ui/button";
import { Send } from "lucide-react";
import 'tailwindcss/tailwind.css';


export default function Chatbot() {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState("");
    const [isTyping, setIsTyping] = useState(false);
    const [darkMode, setDarkMode] = useState(false);
  
    const sendMessage = async () => {
      if (!input.trim()) return;
      
      const userMessage = { sender: "user", text: input };
      setMessages((prevMessages) => [...prevMessages, userMessage]);
      setInput("");
      setIsTyping(true);
  
      try {
        const response = await fetch("http://127.0.0.1:8000/api/chatbot/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ pregunta: input })
        });
  
        const data = await response.json();
        const botMessages = [{ sender: "bot", text: data.mensaje }];
  
        if (data.productos && data.productos.length > 0) {
          botMessages.push({ sender: "bot", text: "📌 Productos encontrados:" });
          data.productos.forEach((producto) => {
            let detalles = `- ${producto.producto}`;
            if (producto.stock !== undefined) detalles += ` | Stock: ${producto.stock}`;
            if (producto.precio !== undefined) detalles += ` | Precio: ${producto.precio}`;
            if (producto.marca !== undefined) detalles += ` | Marca: ${producto.marca}`;
            botMessages.push({ sender: "bot", text: detalles });
          });
        }
  
        setMessages((prevMessages) => [...prevMessages, ...botMessages]);
      } catch (error) {
        setMessages((prevMessages) => [
          ...prevMessages,
          { sender: "bot", text: "⚠️ Error al conectar con el servidor" }
        ]);
      } finally {
        setIsTyping(false);
      }
    };
  
    return (
      <div className={`flex flex-col items-center justify-center min-h-screen ${darkMode ? "bg-gray-900 text-white" : "bg-gray-100 text-black"} p-4 transition-colors`}>
        <Button variant="ghost" onClick={() => setDarkMode(!darkMode)}>
          {darkMode ? "☀️ Modo Claro" : "🌙 Modo Oscuro"}
        </Button>
        <Card className={`w-full max-w-md shadow-lg ${darkMode ? "bg-gray-800" : "bg-white"}`}>
          <CardContent className="p-4 space-y-4">
            <div className="h-80 overflow-y-auto border-b pb-4 flex flex-col space-y-2 p-2">
              {messages.map((msg, index) => (
                <div key={index} className={`max-w-[75%] p-3 rounded-xl shadow-md ${msg.sender === "user" ? "bg-blue-500 text-white self-end" : "bg-gray-200 text-gray-900 self-start"}`}>
                  {msg.text}
                </div>
              ))}
              {isTyping && (
                <div className="bg-gray-200 text-gray-900 self-start p-3 rounded-xl shadow-md flex gap-1">
                  <span className="w-2 h-2 bg-gray-500 rounded-full animate-pulse"></span>
                  <span className="w-2 h-2 bg-gray-500 rounded-full animate-pulse delay-150"></span>
                  <span className="w-2 h-2 bg-gray-500 rounded-full animate-pulse delay-300"></span>
                </div>
              )}
            </div>
            <div className="flex gap-2">
            <Input 
  className="bg-white text-black placeholder-gray-500 border border-gray-400 focus:ring focus:ring-blue-500 dark:bg-white dark:text-black" 
  value={input} 
  onChange={(e) => setInput(e.target.value)} 
  placeholder="Escribe tu pregunta..." 
/>
              <Button onClick={sendMessage}><Send /></Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
}

