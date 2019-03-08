import java.util.ArrayList;

public class Main {
    public static void main(String[] args) {
        DSBMobile dsbMobile = new DSBMobile("", "");
        ArrayList<TimeTable> timeTables = dsbMobile.getTimeTables();
        for (TimeTable timeTable : timeTables) {

            Boolean isHtml = timeTable.IsHtml();

            String date = timeTable.getDate();
            String groupName = timeTable.getGroupName();
            String title = timeTable.getTitle();
            String url = timeTable.getUrl();

        }
    }
}
