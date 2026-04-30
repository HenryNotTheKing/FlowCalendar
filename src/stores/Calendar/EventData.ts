import { ScheduleEvent, Rect} from "../../types/schedule";
import { defineStore } from "pinia";
import { ref } from "vue";

   
 
export const EventData = defineStore("eventData", () => {
    interface ColorOption {
  [key: string]: string;
}

    const colorOptions: ColorOption[] = [
      {'Blue':'#409EFF'},
      {'Green':'#67C23A'},
      {'Yellow':'#E6A23C'},
      {'Red':'#E91E63'},
      {'Purple':'#9C27B0'},
    ];
    const previewColors: ColorOption[] = [
      {'Blue':'color-mix(in srgb, #409EFF 20%, white)'},
      {'Green':'color-mix(in srgb, #67C23A 20%, white)'},
      {'Yellow':'color-mix(in srgb, #E6A23C 20%, white)'},
      {'Red':'color-mix(in srgb, #E91E63 20%, white)'},
      {'Purple':'color-mix(in srgb, #9C27B0 20%, white)'},
    ];
    const darkPreviewColors: ColorOption[] = [
      {'Blue':'color-mix(in srgb, #409EFF 20%, #1e1e1e)'},
      {'Green':'color-mix(in srgb, #67C23A 20%, #1e1e1e)'},
      {'Yellow':'color-mix(in srgb, #E6A23C 20%, #1e1e1e)'},
      {'Red':'color-mix(in srgb, #E91E63 20%, #1e1e1e)'},
      {'Purple':'color-mix(in srgb, #9C27B0 20%, #1e1e1e)'},
    ];
    const colorMap = <Record<string, Record<string, string>>>{
        'Blue': deriveColors('#409EFF'),
        'Green': deriveColors('#67C23A'),
        'Yellow': deriveColors('#E6A23C'),
        'Red': deriveColors('#E91E63'),
        'Purple': deriveColors('#9C27B0'),
        '': deriveColors('#409EFF'),
      }
      const darkColorMap = <Record<string, Record<string, string>>>{
        'Blue': deriveDarkColors('#409EFF'),
        'Green': deriveDarkColors('#67C23A'),
        'Yellow': deriveDarkColors('#E6A23C'),
        'Red': deriveDarkColors('#E91E63'),
        'Purple': deriveDarkColors('#9C27B0'),
      }
      // 添加颜色派生函数
      function deriveColors(baseColor: string) {
        return {
          '--baseColor': baseColor,
          '--shallow': `color-mix(in srgb, ${baseColor} 20%, white)`,
          '--deep': `color-mix(in srgb, ${baseColor} 100%, black)`,
          '--shadow': `color-mix(in srgb, ${baseColor} 70%, black)`,
          '--text': `color-mix(in srgb, ${baseColor} 45%, black)`
        }
      }
      
      // 添加暗色主题颜色派生函数
      function deriveDarkColors(baseColor: string) {
        return {
          '--baseColor': baseColor,
          '--shallow': `color-mix(in srgb, ${baseColor} 30%, #1e1e1e)`,
          '--deep': `color-mix(in srgb, ${baseColor} 100%, #969696)`,
          '--shadow': `color-mix(in srgb, ${baseColor} 70%, #464646)`,
          '--text': `color-mix(in srgb, ${baseColor} 80%, #3e3e3e)`
        }
      }
    const currentRects = ref<Rect[]>([]);
    const selectedRectIndex = ref<number>(-1);
    const currentWeekEvents = ref<ScheduleEvent[]>([]);

    const currentEvent = ref<ScheduleEvent>({
        id: "",
        title: "",
        start: new Date(),
        end: new Date(),
        location: "",
        description: "",
        category: "",
        allDay: false,
        repeat: false,
        recurrence: {
            type: "daily",
            interval: 1,
            endCondition: "occurrences",
            occurrences: 1,
            daysOfWeek: []
        },
        originalEventId: "",
        exceptions: []
    });
    const resetRecurrence = () => {
        currentEvent.value.recurrence = {
            type: "daily",
            interval: 1,
            endCondition: "occurrences",
            occurrences: 1,
            daysOfWeek: []
        }
        return currentEvent.value.recurrence;
    }
    const resetCurrentEvent = () => {
        currentEvent.value = {
            id: "",
            title: "",
            start: new Date(),
            end: new Date(),
            location: "",
            description: "",
            category: "",
            allDay: false,
            repeat: false,
            recurrence: resetRecurrence(),
            originalEventId: "",
            exceptions: []
        }
    }
    return {
        currentRects,
        selectedRectIndex,
        currentWeekEvents,
        currentEvent,
        colorMap,
        darkColorMap,
        colorOptions,
        previewColors,
        darkPreviewColors,
        resetRecurrence,
        resetCurrentEvent
    }
})