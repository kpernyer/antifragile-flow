import { getApiUrl } from '../config/defaults';

// Mock inbox data for demo
const mockInboxData = {
  inbox: [
    {
      id: 1,
      from: 'john.smith@globex-industrial-group.com',
      subject: 'Q4 Financial Review Meeting',
      body: 'Hi Mary,\n\nI wanted to schedule our Q4 financial review meeting. Please let me know your availability for next week.\n\nBest regards,\nJohn'
    },
    {
      id: 2,
      from: 'sarah.johnson@globex-industrial-group.com',
      subject: 'New Product Launch Strategy',
      body: 'Mary,\n\nAttached is the draft strategy for our new product launch. I would appreciate your technical input on the implementation timeline.\n\nThanks,\nSarah'
    },
    {
      id: 3,
      from: 'mike.davis@globex-industrial-group.com',
      subject: 'Client Meeting Follow-up',
      body: 'Hi Mary,\n\nFollowing up on yesterday\'s client meeting. The client is interested in our technical capabilities. Can you prepare a brief technical overview?\n\nMike'
    },
    {
      id: 4,
      from: 'lisa.wilson@globex-industrial-group.com',
      subject: 'Team Building Event Planning',
      body: 'Hello everyone,\n\nWe\'re planning a team building event for next month. Please share your preferences for activities and dates.\n\nLisa'
    }
  ]
};

export const getInbox = async (userId: string): Promise<{ inbox: any[] }> => {
  // Mock data for demo - replace with actual API call when backend is ready
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve(mockInboxData);
    }, 500);
  });

  // Uncomment below for actual API integration:
  // const apiUrl = getApiUrl();
  // const response = await fetch(`${apiUrl}/inbox/${userId}`);
  // if (!response.ok) {
  //   throw new Error('Failed to fetch inbox');
  // }
  // return response.json();
};
