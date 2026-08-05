import { render, screen } from '@testing-library/react';
import App from './App';


global.fetch = jest.fn(() =>
  Promise.resolve({
    ok: true,
    json: () =>
      Promise.resolve([
        {
          id: 1,
          title: "Docker",
          description: "Learn Docker containers"
        }
      ]),
  })
);


test('renders DevOps learning platform home page', async () => {

  render(<App />);

  const heading = await screen.findByText(/Welcome to DevOps Learning Platform/i);

  expect(heading).toBeInTheDocument();

});

test('displays available quiz topics', async () => {

  render(<App />);

  expect(
    await screen.findByText("Docker")
  ).toBeInTheDocument();

});