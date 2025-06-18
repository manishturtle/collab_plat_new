'use client';

import { useChat as useChatContext } from '@/context/chatContext';

/**
 * 
 * Hooks:
  Created a custom useChat hook for easy access to chat functionality
 * 
 */

export const useChat = () => {
  return useChatContext();
};

export default useChat;
