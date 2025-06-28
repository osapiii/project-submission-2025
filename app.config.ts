export default defineAppConfig({
  ui: {
    colors: {
      primary: "sky",
      info: "blue",
      warning: "yellow",
      success: "green",
      error: "red",
      background: "gray",
      neutral: "slate",
      accent: "orange",
      excel: "#197141",
      purple: "#8b5cf6",
    },
    button: {
      slots: {
        base: "font-bold cursor-pointer rounded-lg",
      },
    },
    toast: {
      slots: {
        title: "font-bold text-md",
        wrapper: "p-2",
      },
    },
    stepper: {
      slots: {
        title: "text-white font-bold",
      },
    },
    table: {
      slots: {
        base: "bg-white p-2 rounded-lg shadow-xl",
        th: "text-white bg-slate-700",
      },
    },
    skeleton: {
      background: "bg-background-200",
    },
    modal: {
      slots: {
        content: "min-w-[60vw] overflow-y-scroll",
      },
    },
    card: {
      slots: {
        header: "bg-slate-800 text-white font-bold rounded-t-lg",
      },
    },
    tabs: {
      base: "bg-background-300",
      list: {
        height: "h-10",
        padding: "p-1",
        background: "bg-background-300",
        marker: {
          background: "bg-slate-50",
        },
      },
    },
  },
});
