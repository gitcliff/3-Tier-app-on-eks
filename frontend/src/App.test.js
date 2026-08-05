import { render, screen } from '@testing-library/react';
import App from './App';


beforeEach(() => {

  global.fetch = jest.fn(() =>
    Promise.resolve({
      ok: true,
      json: async () => [
        {
          id: 1,
          title: "Docker",
          description: "Learn Docker containers"
        }
      ],
    })
  );

});


afterEach(() => {
  jest.clearAllMocks();
});


test('renders DevOps learning platform home page', async () => {

  render(<App />);

  expect(
    await screen.findByText(
      /Welcome to DevOps Learning Platform/i
    )
  ).toBeInTheDocument();

});


test('displays available quiz topics', async () => {

  render(<App />);

  expect(
    await screen.findByText("Docker")
  ).toBeInTheDocument();

});