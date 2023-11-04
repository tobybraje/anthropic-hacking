export const getApiResponse = async (
  messages: Record<string, string>[],
): Promise<string> => {
  let request_data: { [id: string]: Record<string, string>[] } = {
    messages: [],
  };
  request_data["messages"] = messages;

  const response = await fetch("http://127.0.0.1:8000/", {
    method: "POST",
    headers: {
      accept: "application/json",
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request_data),
  });

  const responseData = await response.json();
  const responseContent = responseData["response"];
  console.log(request_data);
  return responseContent;
};
