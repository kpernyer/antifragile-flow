import React, { useState, useEffect } from 'react';
import { Box, Grid, List, ListItemText, ListItemButton, Paper, Typography, Divider, CircularProgress } from '@mui/material';
import { getInbox } from '../../api/inbox';
import './Inbox.css';

interface Email {
  id: number;
  from: string;
  subject: string;
  body: string;
}

const Inbox: React.FC = () => {
  const [selectedEmail, setSelectedEmail] = useState<Email | null>(null);
  const [emails, setEmails] = useState<Email[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchInbox = async () => {
      try {
        const data = await getInbox('mary.okeefe@globex-industrial-group.com');
        setEmails(data.inbox);
        if (data.inbox.length > 0) {
          setSelectedEmail(data.inbox[0]);
        }
      } catch (err) {
        setError('Failed to fetch inbox');
      }
      setLoading(false);
    };

    fetchInbox();
  }, []);

  if (loading) {
    return <CircularProgress />;
  }

  if (error) {
    return <Typography color="error">{error}</Typography>;
  }

  return (
    <div className="inbox-container">
      <Typography variant="h4" gutterBottom>
        Inbox
      </Typography>
      <Paper elevation={3}>
        <Grid container>
          <Grid size={4} className="email-list-container">
            <List>
              {emails.map((email) => (
                <ListItemButton
                  key={email.id}
                  onClick={() => setSelectedEmail(email)}
                  selected={selectedEmail?.id === email.id}
                >
                  <ListItemText primary={email.subject} secondary={email.from} />
                </ListItemButton>
              ))}
            </List>
          </Grid>
          <Grid size={8} className="email-content-container">
            {selectedEmail ? (
              <Box p={2}>
                <Typography variant="h5" gutterBottom>
                  {selectedEmail.subject}
                </Typography>
                <Typography variant="subtitle1" gutterBottom>
                  From: {selectedEmail.from}
                </Typography>
                <Divider />
                <Typography variant="body1" style={{ marginTop: '1rem' }}>
                  {selectedEmail.body}
                </Typography>
              </Box>
            ) : (
              <Box p={2}>
                <Typography>Select an email to read</Typography>
              </Box>
            )}
          </Grid>
        </Grid>
      </Paper>
    </div>
  );
};

export default Inbox;
